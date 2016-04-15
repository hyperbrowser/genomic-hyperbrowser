(function() {
	'use strict';
	var Controller = require('./controllers/modeCTRL'),
			ModeModel  = require('./models/modeModel'),
			ModeView   = require('./views/modeView'),
			storage    = require('simplestorage.js'),
			config 		 = require('./stateAppConfig');

	var modeApp = (function() {
		return {
			attachModeListeners: function(modeModel) {
				var mainFrame = $(config.mainFrame), mainContent, mainDocument;
				// Attach listener on home logo to clear
				$(config.hblogo).on('click', function(event) {
					var tmpMode = storage.get('mode');
					storage.flush();
					storage.set('mode', tmpMode);
				});
				// Attach toggle mode functionality on frame border arrow
				$(config.toolBorder).on('click', function(event) {
					modeModel.toggleMode();
				}); 
				// Attach mode functionality to basic and advanced sections on gsuite main welcome page
				mainFrame.on('load', function(e) {
					mainContent  = $($(config.mainFrame)[0]).contents();
					mainDocument = mainContent.filter(function() {
								return this.nodeType === 9;
							});
					var tab1 = mainContent.find(config.tab1);
						if(tab1.length > 0) {
							tab1.find(config.basic).on('click', function() {
								modeModel.toggleMode({'mode': 'basic', 'triggerState': 'history'});
							});
							tab1.find(config.advanced).on('click', function() {
								modeModel.toggleMode({'mode': 'advanced', 'triggerState': 'history'});
							});
						}
				});  
			},
			start: function() {
				var modeCTRL = Object.create(Controller),
				masthead   = $(config.mainNav).first(),
				modeModel  = Object.create(ModeModel),
				modeView   = Object.create(ModeView);

				this.attachModeListeners(modeModel);
			
				// hide Analyse data tab
				masthead.find('td').first().hide();
				
				modeModel.initialize({mode: 'basic'});
				modeView.init({model: modeModel, tagName: 'td', classNames: 'tab'});
				modeView.render();
				masthead.prepend(modeView.el);
				masthead.find('td').first().addClass('active');
				modeCTRL.init({model: modeModel});
				
				return modeModel;
			}
		}
	}());
module.exports = modeApp;
}());

