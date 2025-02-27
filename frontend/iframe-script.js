document.addEventListener('contextmenu', function (event) {
    event.preventDefault();
    function getElementXPath(element) {
        if (!element) return '';
        if (element.id) {
            return '//*[@id="' + element.id + '"]';
        }
        if (element === element.ownerDocument.documentElement) {
            return '/' + element.tagName.toLowerCase();
        }
        let ix = 0;
        const siblings = element.parentNode.childNodes;
        for (let i = 0; i < siblings.length; i++) {
            const sibling = siblings[i];
            if (sibling === element) {
                return getElementXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
            }
            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                ix++;
            }
        }
    }
    const xpath = getElementXPath(event.target);
    window.parent.postMessage({ type: 'xpath', xpath: xpath }, '*');
});