
// Waits for the content of the web page to load
window.addEventListener('DOMContentLoaded', (event) => {
    // When content is loaded, iterate through all the elements with class 'card-img-top'
    document.querySelectorAll('.card-img-top').forEach(img => {
        // Add an event listener to each element that triggers when the element is clicked
        img.addEventListener('click', function() {
            // When the image is clicked, the function is triggered
            // this = the element that triggered the event
            // this.dataset = the data attributes of the element that triggered the event
            // this.dataset.boatId = the value of the data-boat-id attribute of the element that triggered the event
            var boatID = this.dataset.boatId;

            // Redirect to the boat page with the boatID as a parameter
            window.location.href = '/show_boat?id=' + boatID;
        });
    });
});

