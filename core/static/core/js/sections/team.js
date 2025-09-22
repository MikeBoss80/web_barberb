/**
 * TEAM SECTION - Minimal JavaScript Interactions
 * Provides subtle hover effects only
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // Initialize team section
    initTeamSection();

    function initTeamSection() {
        const teamCards = document.querySelectorAll('.team-card');
        const founderBadges = document.querySelectorAll('.founder-badge');
        
        // Add smooth hover effects to cards
        teamCards.forEach((card, index) => {
            setupCardInteractions(card);
        });

        // Add pulse effect to founder badges
        founderBadges.forEach(badge => {
            setupFounderBadgeEffect(badge);
        });
    }

    function setupCardInteractions(card) {
        const image = card.querySelector('.team-image');
        const content = card.querySelector('.team-content');
        
        card.addEventListener('mouseenter', function() {
            // Subtle scale effect on image
            if (image) {
                image.style.transform = 'scale(1.05)';
            }
            
            // Slight lift effect on content
            if (content) {
                content.style.transform = 'translateY(-2px)';
            }
        });

        card.addEventListener('mouseleave', function() {
            // Reset transforms
            if (image) {
                image.style.transform = 'scale(1)';
            }
            
            if (content) {
                content.style.transform = 'translateY(0)';
            }
        });
    }

    function setupFounderBadgeEffect(badge) {
        // Add subtle pulse animation to founder badges
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.boxShadow = '0 6px 20px rgba(62, 26, 78, 0.6)';
        });

        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '0 4px 15px rgba(62, 26, 78, 0.4)';
        });
    }

    // Add CSS classes for smooth transitions
    const style = document.createElement('style');
    style.textContent = `
        .team-image,
        .team-content {
            transition: transform 0.3s ease;
        }
        
        .founder-badge {
            transition: all 0.3s ease;
        }
    `;
    document.head.appendChild(style);
});
