function getElementByXpath(path) {
    return document.evaluate(path, document, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);
}
var elements = []
var xpr = getElementByXpath(arguments[0]); // XPathResult object
for(;;){
    var item = xpr.iterateNext(); // null or DOM element
    if (item) {
	elements.push(item);
    } else {
	break;
    };
};
return elements
