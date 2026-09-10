/**
 * Client-Side JavaScript for Farmer Collaboration & Mandi Marketplace (Farmer Connect)
 */

window.FarmerConnectUI = {
    init: function () {
        console.log("[Farmer Connect] UI initialized successfully.");
    },

    toggleLike: function (postId, btnElement) {
        const countSpan = btnElement.querySelector('.like-count');
        let currentLikes = parseInt(countSpan.innerText || '0');
        
        if (btnElement.classList.contains('liked')) {
            btnElement.classList.remove('liked');
            btnElement.style.color = '#64748b';
            countSpan.innerText = Math.max(0, currentLikes - 1);
        } else {
            btnElement.classList.add('liked');
            btnElement.style.color = '#e11d48';
            countSpan.innerText = currentLikes + 1;
        }
    },

    openInquiryModal: function (listingTitle, sellerName) {
        const msg = prompt(`Send inquiry to ${sellerName} regarding "${listingTitle}":`, `Hello ${sellerName}, I am interested in purchasing this product. Please share availability details.`);
        if (msg) {
            alert(`Inquiry sent successfully to ${sellerName}! You will be notified when they reply.`);
        }
    },

    openCollaborationModal: function (farmerName) {
        const purpose = prompt(`Collaborate with ${farmerName}\nChoose purpose: Bulk Purchase, Equipment Sharing, Transport, Seed Exchange:`, "Equipment Sharing");
        if (purpose) {
            alert(`Collaboration request sent to ${farmerName} for '${purpose}'!`);
        }
    }
};

document.addEventListener("DOMContentLoaded", function () {
    FarmerConnectUI.init();
});
