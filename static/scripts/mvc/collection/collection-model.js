define(["mvc/dataset/dataset-model","mvc/base-mvc","utils/localization"],function(a,b){var c="collections",d={defaults:{model_class:"DatasetCollectionElement",element_identifier:null,element_index:null,element_type:null},_mergeObject:function(a){return _.extend(a,a.object,{element_id:a.id}),delete a.object,a},constructor:function(a){a=this._mergeObject(a),this.idAttribute="element_id",Backbone.Model.apply(this,arguments)},parse:function(a){var b=a;return b=this._mergeObject(b)}},e=Backbone.Model.extend(b.LoggableMixin).extend(d).extend({_logNamespace:c}),f=Backbone.Collection.extend(b.LoggableMixin).extend({_logNamespace:c,model:e,initialize:function(a,b){this.debug(this+"(DCECollection).initialize:",a,b),b=b||{}},toString:function(){return["DatasetCollectionElementCollection(",this.length,")"].join("")}}),g=a.DatasetAssociation.extend(b.mixin(d,{url:function(){return this.has("history_id")?Galaxy.root+"api/histories/"+this.get("history_id")+"/contents/"+this.get("id"):(console.warn("no endpoint for non-hdas within a collection yet"),Galaxy.root+"api/datasets")},defaults:_.extend({},a.DatasetAssociation.prototype.defaults,d.defaults),constructor:function(a,b){this.debug("	 DatasetDCE.constructor:",a,b),d.constructor.call(this,a,b)},initialize:function(b,c){this.debug(this+"(DatasetDCE).initialize:",b,c),a.DatasetAssociation.prototype.initialize.call(this,b,c)},hasDetails:function(){return _.has(this.attributes,"annotation")},toString:function(){var a=this.get("element_identifier");return["DatasetDCE(",a,")"].join("")}})),h=f.extend({model:g,initialize:function(a,b){this.debug(this+"(DatasetDCECollection).initialize:",a,b),f.prototype.initialize.call(this,a,b)},toString:function(){return["DatasetDCECollection(",this.length,")"].join("")}}),i=Backbone.Model.extend(b.LoggableMixin).extend(b.SearchableModelMixin).extend({_logNamespace:c,defaults:{collection_type:null,deleted:!1},collectionClass:f,initialize:function(a,b){this.debug(this+"(DatasetCollection).initialize:",a,b,this),this.elements=this._createElementsModel(),this.on("change:elements",function(){this.log("change:elements"),this.elements=this._createElementsModel()})},_createElementsModel:function(){this.debug(this+"._createElementsModel",this.collectionClass,this.get("elements"),this.elements);var a=this.get("elements")||[];return this.unset("elements",{silent:!0}),this.elements=new this.collectionClass(a),this.elements},toJSON:function(){var a=Backbone.Model.prototype.toJSON.call(this);return this.elements&&(a.elements=this.elements.toJSON()),a},inReadyState:function(){var a=this.get("populated");return this.isDeletedOrPurged()||a},hasDetails:function(){return this.debug("hasDetails:",this.elements.length),0!==this.elements.length},getVisibleContents:function(){return this.elements},"delete":function(a){return this.get("deleted")?jQuery.when():this.save({deleted:!0},a)},undelete:function(a){return!this.get("deleted")||this.get("purged")?jQuery.when():this.save({deleted:!1},a)},isDeletedOrPurged:function(){return this.get("deleted")||this.get("purged")},searchAttributes:["name"],toString:function(){var a=[this.get("id"),this.get("name")||this.get("element_identifier")];return"DatasetCollection("+a.join(",")+")"}}),j=i.extend({collectionClass:h,initialize:function(a,b){this.debug(this+"(ListDatasetCollection).initialize:",a,b),i.prototype.initialize.call(this,a,b)},toString:function(){return["ListDatasetCollection(",this.get("name"),")"].join("")}}),k=j.extend({initialize:function(a,b){this.debug(this+"(PairDatasetCollection).initialize:",a,b),j.prototype.initialize.call(this,a,b)},toString:function(){return["PairDatasetCollection(",this.get("name"),")"].join("")}}),l=i.extend(b.mixin(d,{constructor:function(a,b){this.debug("	 NestedDCDCE.constructor:",a,b),d.constructor.call(this,a,b)},toString:function(){var a=this.object?""+this.object:this.get("element_identifier");return["NestedDCDCE(",a,")"].join("")}})),m=f.extend({model:l,initialize:function(a,b){this.debug(this+"(NestedDCDCECollection).initialize:",a,b),f.prototype.initialize.call(this,a,b)},toString:function(){return["NestedDCDCECollection(",this.length,")"].join("")}}),n=k.extend(b.mixin(d,{constructor:function(a,b){this.debug("	 NestedPairDCDCE.constructor:",a,b),d.constructor.call(this,a,b)},toString:function(){var a=this.object?""+this.object:this.get("element_identifier");return["NestedPairDCDCE(",a,")"].join("")}})),o=m.extend({model:n,initialize:function(a,b){this.debug(this+"(NestedPairDCDCECollection).initialize:",a,b),m.prototype.initialize.call(this,a,b)},toString:function(){return["NestedPairDCDCECollection(",this.length,")"].join("")}}),p=i.extend({collectionClass:o,initialize:function(a,b){this.debug(this+"(ListPairedDatasetCollection).initialize:",a,b),i.prototype.initialize.call(this,a,b)},toString:function(){return["ListPairedDatasetCollection(",this.get("name"),")"].join("")}});return{ListDatasetCollection:j,PairDatasetCollection:k,ListPairedDatasetCollection:p}});
//# sourceMappingURL=../../../maps/mvc/collection/collection-model.js.map