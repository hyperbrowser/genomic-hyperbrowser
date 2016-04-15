(function(){
	'use strict';
	var BaseView = require('../prototypes/viewPrototype'),
	_    = require('underscore'),
	storage    = require('simplestorage.js');

	var ModeView = Object.create(BaseView);

	_.extend(ModeView, (function() {
			// private variables
			// Self is needed because the parseEvent method is called from a click event and not from this object,
			// shadowing the this keyword.
			var self;
			return {
				template: _.template(
					'<a target="_self" id="mode" class="noLink" href="" ><%= this.toggleViewText(mode)%></a>' 
					 + '<div class="submenu">'
           	 + '<ul>'
               + '<li class="<%= (mode === "basic"? "disabledMode": "") %>"><a href="" id="basic">Basic mode</a></li>'
               + '<li class="<%= (mode === "advanced"? "disabledMode": "") %>"><a href="" id="advanced">Advanced mode</a></li>'
             + '</ul>'
           + '</div>'
					),
				initialize: function(options) {
					this.eventSetup();
					self = this;
				},
				eventSetup: function() {
					this.$el.click(this.parseEvent);
					this.listenTo('change:mode', this.update, this);
					this.listenTo('change:history', this.update, this);
				},
				parseEvent: function(event) {
					event.preventDefault();
					event.stopPropagation();
					var attr = event.target.id;
					if(attr !== 'mode') {
						self.model.toggleMode({mode: attr, triggerState: 'history'});
					}
				},
				render: function(props) {
					var attributes = this.model.toJSON();
					this.$el.html(this.template(attributes));
					return this;
				},
				toggleViewText: function(text) {
					return (text === "basic" ? "Mode: Basic" : "Mode: Advanced");
				},
				update: function() {
					this.render();
				}
			}
		}())
	);

	module.exports = ModeView; 

}());