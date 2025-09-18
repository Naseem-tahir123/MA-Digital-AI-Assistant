(function(w,d) {
    class AssortChatEmbed {
        constructor(config = {}) {
            this.config = {
                apiUrl: config.apiUrl || 'http://localhost:8000',
                position: config.position || 'bottom-right',
                primaryColor: config.primaryColor || '#db152f',
                title: config.title || 'AssortTech Chat'
            };
            this.isOpen = false;
            this.init();
        }

        init() {
            this.createStyles();
            this.createToggleButton();
            this.createWidget();
        }

        createStyles() {
            const css = `
                .assort-widget-hidden {
                    display: none !important;
                }

                #assort-chat-widget {
                    position: fixed;
                    ${this.config.position.includes('bottom') ? 'bottom: 80px;' : 'top: 20px;'}
                    ${this.config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
                    z-index: 999998;
                    display: none;
                    transition: all 0.3s ease;
                }

                #assort-chat-toggle {
                    position: fixed;
                    ${this.config.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
                    ${this.config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: ${this.config.primaryColor};
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    cursor: pointer;
                    z-index: 999999;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: transform 0.3s ease;
                }

                #assort-chat-toggle:hover {
                    transform: scale(1.1);
                }

                #assort-chat-close {
                    position: absolute;
                    top: 5px;
                    right: 5px;
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.2);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 999999;
                    transition: transform 0.2s ease;
                }

                #assort-chat-close:hover {
                    transform: scale(1.1);
                }
            `;
            const style = d.createElement('style');
            style.textContent = css;
            d.head.appendChild(style);
        }

        createToggleButton() {
            const button = d.createElement('div');
            button.id = 'assort-chat-toggle';
            button.innerHTML = `
                <svg viewBox="0 0 24 24" width="24" height="24" fill="white">
                    <path d="M20,2H4C2.9,2,2,2.9,2,4v18l4-4h14c1.1,0,2-0.9,2-2V4C22,2.9,21.1,2,20,2z"/>
                </svg>
            `;
            button.onclick = () => this.toggleWidget();
            d.body.appendChild(button);
        }

        createWidget() {
            const container = d.createElement('div');
            container.id = 'assort-chat-widget';
            
            const closeBtn = d.createElement('div');
            closeBtn.id = 'assort-chat-close';
            closeBtn.innerHTML = `
                <svg viewBox="0 0 24 24" width="16" height="16" fill="white">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
            `;
            closeBtn.onclick = () => this.closeWidget();
            
            const iframe = d.createElement('iframe');
            iframe.src = `${this.config.apiUrl}/widget`;
            iframe.style.width = '350px';
            iframe.style.height = '500px';
            iframe.style.border = 'none';
            iframe.style.borderRadius = '10px';
            iframe.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
            
            container.appendChild(closeBtn);
            container.appendChild(iframe);
            d.body.appendChild(container);
        }

        toggleWidget() {
            const widget = d.getElementById('assort-chat-widget');
            const toggle = d.getElementById('assort-chat-toggle');
            this.isOpen = !this.isOpen;
            
            widget.style.display = this.isOpen ? 'block' : 'none';
            toggle.style.transform = this.isOpen ? 'scale(0)' : 'scale(1)';
            toggle.style.opacity = this.isOpen ? '0' : '1';
        }

        closeWidget() {
            const widget = d.getElementById('assort-chat-widget');
            const toggle = d.getElementById('assort-chat-toggle');
            this.isOpen = false;
            
            widget.style.display = 'none';
            toggle.style.transform = 'scale(1)';
            toggle.style.opacity = '1';
        }
    }

    w.AssortChatEmbed = AssortChatEmbed;
})(window, document);

 