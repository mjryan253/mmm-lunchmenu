/* global Module */

/* MMM-LunchMenu
 * A MagicMirror² module to display lunch menu HTML file
 * Works with an external scraper service to fetch and parse menu data
 */

Module.register("MMM-LunchMenu", {
    defaults: {
        menuUrl: "/modules/MMM-LunchMenu/public/lunch_menu.html",
        updateInterval: 3600000, // 1 hour in milliseconds
        width: "600px",
        height: "400px"
    },

    start: function() {
        this.menuContent = null;
        this.loading = true;
        this.loadMenu();
        this.scheduleUpdate();
    },

    scheduleUpdate: function() {
        var self = this;
        setInterval(function() {
            self.loadMenu();
        }, this.config.updateInterval);
    },

    loadMenu: function() {
        var self = this;
        this.loading = true;
        this.updateDom();
        
        // Fetch the menu file via HTTP (MagicMirror serves static files)
        fetch(this.config.menuUrl)
            .then(function(response) {
                if (!response.ok) {
                    throw new Error("HTTP " + response.status);
                }
                return response.text();
            })
            .then(function(html) {
                self.menuContent = html;
                self.loading = false;
                self.updateDom();
            })
            .catch(function(error) {
                console.error("MMM-LunchMenu: Error loading menu file:", error);
                self.menuContent = "<div style='padding: 20px; text-align: center; color: #fff;'>Menu not available yet. Please wait...</div>";
                self.loading = false;
                self.updateDom();
            });
    },

    getDom: function() {
        var wrapper = document.createElement("div");
        wrapper.style.width = this.config.width;
        wrapper.style.height = this.config.height;
        wrapper.style.overflow = "auto";
        
        if (this.loading && !this.menuContent) {
            wrapper.innerHTML = "<div style='padding: 20px; text-align: center; color: #fff;'>Loading menu...</div>";
        } else if (this.menuContent) {
            wrapper.innerHTML = this.menuContent;
        } else {
            wrapper.innerHTML = "<div style='padding: 20px; text-align: center; color: #fff;'>Loading menu...</div>";
        }
        
        return wrapper;
    }
});

