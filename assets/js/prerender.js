// catch each error in the console and send it to PyQt5
window.onerror = function (msg, url, lineNo, columnNo, error) {

}

function sendErrorToPyQt(errorMsg) {
    if (typeof window.external !== 'undefined') {
        window.external.sendError(errorMsg);
    }
}