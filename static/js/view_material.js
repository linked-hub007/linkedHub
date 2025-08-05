// Global variables
let currentZoom = 1;
let currentPage = 1;
let totalPages = 1;
let pdfDoc = null;
let pdfCanvas = null;
let pdfCtx = null;
let documentType = '';
let fileUrl = '';
let isFullscreen = false;

const ZOOM_FACTOR = 0.2;
const MAX_ZOOM = 5;
const MIN_ZOOM = 0.3;

// Initialize PDF.js with better error handling
function initializePDFJS() {
    if (typeof pdfjsLib !== 'undefined') {
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        return true;
    } else {
        console.error('PDF.js library not loaded');
        return false;
    }
}

// ==================== PROTECTION FUNCTIONS ====================

function disableRightClickOnContent() {
    const contentAreas = [
        document.getElementById('pdf-canvas'),
        document.getElementById('image-viewer'),
        document.getElementById('generic-viewer'),
        document.getElementById('viewer-image')
    ];
    
    contentAreas.forEach(area => {
        if (area) {
            area.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                return false;
            });
        }
    });
}

function disableTextSelectionOnContent() {
    const contentAreas = [
        document.getElementById('pdf-canvas'),
        document.getElementById('image-viewer'),
        document.getElementById('generic-viewer'),
        document.getElementById('viewer-image')
    ];
    
    contentAreas.forEach(area => {
        if (area) {
            area.addEventListener('selectstart', function(e) {
                e.preventDefault();
                return false;
            });
            
            area.style.userSelect = 'none';
            area.style.webkitUserSelect = 'none';
            area.style.mozUserSelect = 'none';
            area.style.msUserSelect = 'none';
        }
    });
}

function disableKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        const isOnContentArea = e.target.closest('#pdf-viewer') || 
                               e.target.closest('#image-viewer') || 
                               e.target.closest('#generic-viewer') ||
                               e.target.id === 'pdf-canvas';
        
        if (isOnContentArea) {
            // Disable Ctrl+A, Ctrl+C, Ctrl+X, Ctrl+S, Ctrl+P
            if ((e.ctrlKey || e.metaKey) && ['a', 'c', 'x', 's', 'p'].includes(e.key.toLowerCase())) {
                e.preventDefault();
                return false;
            }
        }
        
        // Allow navigation shortcuts
        if (!e.ctrlKey && !e.metaKey) {
            switch (e.key) {
                case 'ArrowLeft':
                case 'PageUp':
                    if (documentType === 'pdf') {
                        e.preventDefault();
                        goToPreviousPage();
                    }
                    break;
                case 'ArrowRight':
                case 'PageDown':
                case ' ':
                    if (documentType === 'pdf') {
                        e.preventDefault();
                        goToNextPage();
                    }
                    break;
                case 'Home':
                    if (documentType === 'pdf') {
                        e.preventDefault();
                        goToFirstPage();
                    }
                    break;
                case 'End':
                    if (documentType === 'pdf') {
                        e.preventDefault();
                        goToLastPage();
                    }
                    break;
            }
        }
        
        // Allow zoom shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case '=':
                case '+':
                    e.preventDefault();
                    zoomIn();
                    break;
                case '-':
                    e.preventDefault();
                    zoomOut();
                    break;
                case '0':
                    e.preventDefault();
                    resetZoom();
                    break;
            }
        }
    });
}

function disableImageProtection() {
    const viewerImage = document.getElementById('viewer-image');
    if (viewerImage) {
        viewerImage.addEventListener('dragstart', function(e) {
            e.preventDefault();
            return false;
        });
        
        viewerImage.setAttribute('draggable', 'false');
    }
}

// ==================== UTILITY FUNCTIONS ====================

function hideLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.style.display = 'none';
}

function showLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.style.display = 'flex';
}

function showErrorMessage(message = 'Unable to load document') {
    hideLoadingSpinner();
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.querySelector('p').textContent = message;
        errorElement.classList.remove('hidden');
    }
}

function hideErrorMessage() {
    const errorElement = document.getElementById('error-message');
    if (errorElement) errorElement.classList.add('hidden');
}

function updateZoomDisplay() {
    const percentage = Math.round(currentZoom * 100);
    const zoomDisplay = document.getElementById('zoom-level-display');
    if (zoomDisplay) zoomDisplay.textContent = `${percentage}%`;
}

function updatePageNavigation() {
    const pageInput = document.getElementById('page-input');
    if (pageInput) {
        pageInput.value = currentPage;
        pageInput.max = totalPages;
    }
    
    const totalPagesElement = document.getElementById('total-pages');
    if (totalPagesElement) totalPagesElement.textContent = totalPages;
    
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');
    const firstBtn = document.getElementById('first-page-btn');
    const lastBtn = document.getElementById('last-page-btn');
    
    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
    if (firstBtn) firstBtn.disabled = currentPage <= 1;
    if (lastBtn) lastBtn.disabled = currentPage >= totalPages;
}

function showViewer(type) {
    const pdfViewer = document.getElementById('pdf-viewer');
    const imageViewer = document.getElementById('image-viewer');
    const genericViewer = document.getElementById('generic-viewer');
    const pageNav = document.getElementById('page-nav');
    
    if (pdfViewer) pdfViewer.classList.add('hidden');
    if (imageViewer) imageViewer.classList.add('hidden');
    if (genericViewer) genericViewer.classList.add('hidden');
    if (pageNav) pageNav.classList.add('hidden');
    
    if (type === 'pdf') {
        if (pdfViewer) pdfViewer.classList.remove('hidden');
        if (pageNav) pageNav.classList.remove('hidden');
    } else if (type === 'image') {
        if (imageViewer) imageViewer.classList.remove('hidden');
    } else {
        if (genericViewer) genericViewer.classList.remove('hidden');
    }
}

// FIXED: Updated function to properly handle file types
function getFileTypeFromUrl(url) {
    if (!url) return 'generic';
    
    const extension = url.split('.').pop().toLowerCase().split('?')[0];
    if (extension === 'pdf') return 'pdf';
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'].includes(extension)) return 'image';
    if (['doc', 'docx', 'txt', 'rtf'].includes(extension)) return 'document';
    return 'generic';
}

// FIXED: Updated function to map Django material types to viewer types
function mapMaterialTypeToViewerType(materialType, fileUrl) {
    // If we have a material type from Django, use it
    if (materialType) {
        switch (materialType.toLowerCase()) {
            case 'pdf':
                return 'pdf';
            case 'image':
                return 'image';
            default:
                return 'generic';
        }
    }
    
    // Fallback to URL-based detection
    return getFileTypeFromUrl(fileUrl);
}

function getOptimalPDFScale(page, fitType = 'width') {
    const container = document.querySelector('.pdf-viewer') || document.getElementById('pdf-viewer');
    if (!container) return 1;
    
    const containerWidth = container.clientWidth - 40;
    const containerHeight = container.clientHeight - 40;
    
    const viewport = page.getViewport({ scale: 1 });
    const scaleX = containerWidth / viewport.width;
    const scaleY = containerHeight / viewport.height;
    
    if (fitType === 'width') return Math.min(scaleX, 2);
    if (fitType === 'height') return Math.min(scaleY, 2);
    return Math.min(scaleX, scaleY, 1.5);
}

// ==================== PDF FUNCTIONS ====================

async function renderPDFPage(pageNumber) {
    if (!pdfDoc || !pdfCanvas || !pdfCtx) {
        showErrorMessage('PDF viewer not properly initialized');
        return;
    }
    
    showLoadingSpinner();
    hideErrorMessage();
    
    try {
        const page = await pdfDoc.getPage(pageNumber);
        const viewport = page.getViewport({ scale: currentZoom });
        
        pdfCanvas.width = viewport.width;
        pdfCanvas.height = viewport.height;
        pdfCtx.clearRect(0, 0, pdfCanvas.width, pdfCanvas.height);
        
        const renderContext = {
            canvasContext: pdfCtx,
            viewport: viewport,
            enableWebGL: false
        };
        
        await page.render(renderContext).promise;
        hideLoadingSpinner();
        
    } catch (error) {
        console.error('Error rendering PDF page:', error);
        showErrorMessage(`Error rendering PDF page ${pageNumber}: ${error.message}`);
    }
}

async function loadPDF(url) {
    if (!initializePDFJS()) {
        showErrorMessage('PDF.js library not available');
        return;
    }
    
    showLoadingSpinner();
    hideErrorMessage();
    
    try {
        const loadingTask = pdfjsLib.getDocument({
            url: url,
            cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/cmaps/',
            cMapPacked: true,
            withCredentials: false,
            timeout: 60000
        });
        
        pdfDoc = await loadingTask.promise;
        totalPages = pdfDoc.numPages;
        currentPage = 1;
        
        if (!pdfCanvas) {
            pdfCanvas = document.getElementById('pdf-canvas');
            if (pdfCanvas) pdfCtx = pdfCanvas.getContext('2d');
        }
        
        const page = await pdfDoc.getPage(1);
        currentZoom = getOptimalPDFScale(page, 'width');
        updateZoomDisplay();
        updatePageNavigation();
        await renderPDFPage(currentPage);
        
    } catch (error) {
        console.error('Error loading PDF:', error);
        
        let errorMessage = 'Unable to load PDF document.';
        if (error.name === 'MissingPDFException') {
            errorMessage = 'PDF file not found. Please check the file path.';
        } else if (error.name === 'InvalidPDFException') {
            errorMessage = 'Invalid PDF file. The file may be corrupted.';
        } else if (error.name === 'UnexpectedResponseException') {
            errorMessage = 'Network error. Please check your internet connection.';
        } else if (error.message) {
            errorMessage += ` Error: ${error.message}`;
        }
        
        showErrorMessage(errorMessage);
    }
}

// ==================== IMAGE FUNCTIONS ====================

function loadImage(url) {
    if (!url) {
        showErrorMessage('No image URL provided');
        return;
    }
    
    showLoadingSpinner();
    hideErrorMessage();
    
    const img = document.getElementById('viewer-image');
    if (!img) {
        showErrorMessage('Image viewer element not found');
        return;
    }
    
    img.onload = function() {
        hideLoadingSpinner();
        
        // Set initial zoom to fit width
        const viewer = document.getElementById('image-viewer');
        if (viewer && img.naturalWidth) {
            const viewerWidth = viewer.clientWidth - 40;
            currentZoom = Math.min(viewerWidth / img.naturalWidth, 1);
            applyImageZoom();
            updateZoomDisplay();
        }
    };
    
    img.onerror = function() {
        showErrorMessage('Unable to load image. Please check if the file exists and is accessible.');
    };
    
    // Add cache busting parameter
    const separator = url.includes('?') ? '&' : '?';
    img.src = url + separator + 't=' + new Date().getTime();
}

function applyImageZoom() {
    const img = document.getElementById('viewer-image');
    if (img) {
        img.style.transform = `scale(${currentZoom})`;
        img.style.transformOrigin = 'center center';
    }
}

// ==================== DOCUMENT FUNCTIONS ====================

function loadGenericDocument(url) {
    if (!url) {
        showErrorMessage('No document URL provided');
        return;
    }
    
    showLoadingSpinner();
    hideErrorMessage();
    
    const iframe = document.getElementById('document-frame');
    if (!iframe) {
        showErrorMessage('Document frame element not found');
        return;
    }
    
    iframe.onload = function() {
        hideLoadingSpinner();
    };
    
    iframe.onerror = function() {
        showErrorMessage('Unable to load document. The file may not be supported or accessible.');
    };
    
    // For document viewing, try Google Docs viewer or direct load
    let documentUrl = url;
    if (url.toLowerCase().includes('.doc')) {
        documentUrl = `https://docs.google.com/gview?url=${encodeURIComponent(url)}&embedded=true`;
    }
    
    iframe.src = documentUrl;
}

// ==================== VIEWER CONTROLS ====================

function zoomIn() {
    if (currentZoom < MAX_ZOOM) {
        currentZoom = Math.min(currentZoom + ZOOM_FACTOR, MAX_ZOOM);
        applyZoom();
    }
}

function zoomOut() {
    if (currentZoom > MIN_ZOOM) {
        currentZoom = Math.max(currentZoom - ZOOM_FACTOR, MIN_ZOOM);
        applyZoom();
    }
}

function resetZoom() {
    currentZoom = 1;
    applyZoom();
}

function fitToWidth() {
    if (documentType === 'pdf' && pdfDoc) {
        pdfDoc.getPage(currentPage).then(page => {
            currentZoom = getOptimalPDFScale(page, 'width');
            applyZoom();
        });
    } else if (documentType === 'image') {
        const img = document.getElementById('viewer-image');
        const viewer = document.getElementById('image-viewer');
        if (img && img.naturalWidth && viewer) {
            const viewerWidth = viewer.clientWidth - 40;
            currentZoom = Math.min(viewerWidth / img.naturalWidth, MAX_ZOOM);
            applyZoom();
        }
    }
}

function fitToHeight() {
    if (documentType === 'pdf' && pdfDoc) {
        pdfDoc.getPage(currentPage).then(page => {
            currentZoom = getOptimalPDFScale(page, 'height');
            applyZoom();
        });
    } else if (documentType === 'image') {
        const img = document.getElementById('viewer-image');
        const viewer = document.getElementById('image-viewer');
        if (img && img.naturalHeight && viewer) {
            const viewerHeight = viewer.clientHeight - 40;
            currentZoom = Math.min(viewerHeight / img.naturalHeight, MAX_ZOOM);
            applyZoom();
        }
    }
}

function applyZoom() {
    updateZoomDisplay();
    
    if (documentType === 'pdf') {
        renderPDFPage(currentPage);
    } else if (documentType === 'image') {
        applyImageZoom();
    }
}

// ==================== PAGE NAVIGATION ====================

function goToFirstPage() {
    if (currentPage > 1) {
        currentPage = 1;
        updatePageNavigation();
        renderPDFPage(currentPage);
    }
}

function goToPreviousPage() {
    if (currentPage > 1) {
        currentPage--;
        updatePageNavigation();
        renderPDFPage(currentPage);
    }
}

function goToNextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        updatePageNavigation();
        renderPDFPage(currentPage);
    }
}

function goToLastPage() {
    if (currentPage < totalPages) {
        currentPage = totalPages;
        updatePageNavigation();
        renderPDFPage(currentPage);
    }
}

function goToPage(pageNumber) {
    const page = parseInt(pageNumber);
    if (page >= 1 && page <= totalPages && page !== currentPage) {
        currentPage = page;
        updatePageNavigation();
        renderPDFPage(currentPage);
    }
}

// ==================== FULLSCREEN ====================

function toggleFullscreen() {
    const viewerContainer = document.getElementById('viewer-container');
    if (!viewerContainer) return;
    
    if (!isFullscreen) {
        if (viewerContainer.requestFullscreen) {
            viewerContainer.requestFullscreen();
        } else if (viewerContainer.webkitRequestFullscreen) {
            viewerContainer.webkitRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        }
    }
}

function handleFullscreenChange() {
    isFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement);
    
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    if (fullscreenBtn) {
        const icon = fullscreenBtn.querySelector('i');
        if (icon) {
            icon.className = isFullscreen ? 'fas fa-compress' : 'fas fa-expand';
        }
    }
    
    if (documentType === 'pdf' && pdfDoc) {
        setTimeout(() => renderPDFPage(currentPage), 100);
    }
}

// ==================== INITIALIZATION ====================

// FIXED: Updated initialization to properly handle Django data
function initializeViewer() {
    if (window.documentConfig) {
        const djangoMaterialType = window.documentConfig.materialType; // Add this to your template
        fileUrl = window.documentConfig.fileUrl;
        
        if (!fileUrl) {
            showErrorMessage('No file URL provided in configuration');
            return;
        }
        
        // Use the new mapping function
        documentType = mapMaterialTypeToViewerType(djangoMaterialType, fileUrl);
        
        console.log('Document type:', documentType, 'File URL:', fileUrl); // Debug log
        
        showViewer(documentType);
        
        switch (documentType) {
            case 'pdf':
                pdfCanvas = document.getElementById('pdf-canvas');
                if (pdfCanvas) pdfCtx = pdfCanvas.getContext('2d');
                loadPDF(fileUrl);
                break;
            case 'image':
                loadImage(fileUrl);
                break;
            case 'document':
            case 'generic':
                loadGenericDocument(fileUrl);
                break;
            default:
                showErrorMessage(`Unsupported file type: ${documentType}`);
        }
    } else {
        showErrorMessage('Document configuration not found');
    }
}

function initializeEventListeners() {
    // Protection functions
    disableRightClickOnContent();
    disableTextSelectionOnContent();
    disableKeyboardShortcuts();
    disableImageProtection();
    
    // Fullscreen events
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    
    // Button events
    const buttons = [
        { id: 'zoom-in-btn', handler: zoomIn },
        { id: 'zoom-out-btn', handler: zoomOut },
        { id: 'fit-width-btn', handler: fitToWidth },
        { id: 'fit-height-btn', handler: fitToHeight },
        { id: 'fullscreen-btn', handler: toggleFullscreen },
        { id: 'first-page-btn', handler: goToFirstPage },
        { id: 'prev-page-btn', handler: goToPreviousPage },
        { id: 'next-page-btn', handler: goToNextPage },
        { id: 'last-page-btn', handler: goToLastPage }
    ];
    
    buttons.forEach(({ id, handler }) => {
        const btn = document.getElementById(id);
        if (btn) btn.addEventListener('click', handler);
    });
    
    // Page input
    const pageInput = document.getElementById('page-input');
    if (pageInput) {
        pageInput.addEventListener('change', (e) => goToPage(e.target.value));
        pageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') goToPage(e.target.value);
        });
    }
    
    // Window resize
    window.addEventListener('resize', () => {
        clearTimeout(window.resizeTimeout);
        window.resizeTimeout = setTimeout(() => {
            if (documentType === 'pdf' && pdfDoc) {
                renderPDFPage(currentPage);
            } else if (documentType === 'image') {
                applyImageZoom();
            }
        }, 150);
    });
}

// Main initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    setTimeout(initializeViewer, 100);
});

// Make functions available globally for debugging
if (typeof window !== 'undefined') {
    window.initializeDocumentViewer = initializeViewer;
}