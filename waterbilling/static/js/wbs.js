window.seconds = null;
window.status = null;
window.jobs_done = 0;
window.jobs_total = 100;

$(document).ready(function(){

	$.fn.serializeObject = function()
	{
	    var o = {};
	    var a = this.serializeArray();
	    $.each(a, function() {
	        if (o[this.name] !== undefined) {
	            if (!o[this.name].push) {
	                o[this.name] = [o[this.name]];
	            }
	            o[this.name].push(this.value || '');
	        } else {
	            o[this.name] = this.value || '';
	        }
	    });
	    return o;
	};

	$('.btn-addnote').click(function(e){
		e.preventDefault();
		$('.control-group').removeClass('error');
		$('.help_text').remove();
		//$('.controls').children().val('');
		$('#myNoteModal').modal('show');
		$('#alert_template').hide();

	});

	$('.btn-payment').click(function(e){
		e.preventDefault();
		$('.control-group').removeClass('error');
		$('.help_text').remove();
		//$('.controls').children().val('');
		$('#myPaymentModal').modal({backdrop:'static',keyboard:false});
		$('#myPaymentModal').modal('show');
		$('#alert_template').hide();

	});

	$('.btn-addmeter').click(function(e){
		e.preventDefault();
		$('.control-group').removeClass('error');
		$('.help_text').remove();
		$('.controls').children().val('');
		$('#myMeterModal').modal('show');
		$('#alert_template').hide();

	});

	$('.btn-adjustment').click(function(e){
		e.preventDefault();
		$('.control-group').removeClass('error');
		$('.help_text').remove();
		$('#myAdjustmentModal').modal('show');
	});

	$('#btnConfirmPayment').click(function(e){
		e.preventDefault();
		$('.help_text').remove();

		request = $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'POST',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/payments/',
		    data: $("#paymentForm").serializeObject(),
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Payment','success','',1500);
				//$('#alert_template span').empty();
  				//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn(' ');
				//$('#alert_template').addClass('alert-success');
				//$('#alert_template button').after('<span> Payment Successful. </span>');
				$('#myPaymentModal').modal('hide');
				window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Payment','fail','',1500);
		      	//$('#alert_template span').empty();
		      	//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
  				//$('#alert_template').addClass('alert-error');
		      	//$('#alert_template button').afte                                                                                                                                                                                                                                      p                                                                                                                                                                                                                                                                                                  r('<span> Payment Failed. </span>');
		      	$('.control-group').removeClass('error');
		      	//$('#myPaymentModal').modal('hide');
		      	//$('.control-group').addClass(textStatus);
		      	console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	var p = JSON.parse(request.responseText)
				for (var key in p) {
					if (p.hasOwnProperty(key)) {
						console.log('key and p key', key, p[key]);
						var myfield = 'id_' + key;
						console.log('myfield,', myfield);
						//$('.' + myfield).addClass(textStatus);
						//$('#' + myfield).addClass('alert alert-error');
						$('#' + myfield).parent().parent().addClass(textStatus);
						$('#' + myfield).after('<span class="help_text error"> '+p[key]+'</span>');


					}
				}
		    },
		    dataType: "json"
		  });
		
	});

	$('#btnConfirmAdjustment').click(function(e){
		e.preventDefault();
		$('.help_text').remove();

		request = $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'POST',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/adjustments/',
		    data: $("#adjustmentForm").serializeObject(),
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Adjustment','success','',1500);
				//$('#alert_template span').empty();
  				//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
				//$('#alert_template').addClass('alert-success');
				//$('#alert_template button').after('<span> Adjustment Successful. </span>');
				$('#myAdjustmentModal').modal('hide');
				window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Adjustment','fail','',1500);
		      	//$('#alert_template span').empty();
		      	//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
  				//$('#alert_template').addClass('alert-error');
		      	//$('#alert_template button').after('<span> Adjustment Failed. </span>');
		      	$('.control-group').removeClass('error');
		      	//$('#myPaymentModal').modal('hide');
		      	//$('.control-group').addClass(textStatus);
		      	//console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	var p = JSON.parse(request.responseText)
				for (var key in p) {
					if (p.hasOwnProperty(key)) {
						console.log('key and p key', key, p[key]);
						var myfield = 'id_' + key;
						console.log('myfield,', myfield);
						//$('.' + myfield).addClass(textStatus);
						//$('#' + myfield).addClass('alert alert-error');
						$('#myAdjustmentModal').find('#' + myfield).parent().parent().addClass(textStatus);
						$('#myAdjustmentModal').find('#' + myfield).after('<span class="help_text error"> '+p[key]+'</span>');
					}
				}
		    },
		    dataType: "json"
		  });
	});

	$('#btnConfirmReconnection').click(function(e){

		e.preventDefault();
		console.log("confirm reconnection button clicked");
		$('.help_text').remove();
		//console.log("need to get acct number" + $(this).textContent);
		var now = new Date();
		console.log("now is "+ now.getMonth() + '/' + now.getDate() + '/' + now.getFullYear());
		var nowformat = now.getMonth() + '/' + now.getDate() + '/' + now.getFullYear()

		request = $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'POST',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/adjustments/',
		    data: {'amount': $('#reconnection-fee').val(),
		    	   'type': 'reconnection_fee',
		    	   'description': $('#set-remarks').val(),
		    	   'account': $('#id_account').val(),
		    	   'adjustment_date': nowformat,
		    	    
				},
		    dataType: "json",
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Adjustment for Reconnection','success','',1500);
				setAccountStatusActive()
				$('#myReconnectModal').modal('hide');
				window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Adjustment for Reconnection','fail','',1500);
		      	$('.control-group').removeClass('error');
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	/*var p = JSON.parse(request.responseText)
				for (var key in p) {
					if (p.hasOwnProperty(key)) {
						console.log('key and p key', key, p[key]);
						var myfield = 'id_' + key;
						console.log('myfield,', myfield);
						//$('.' + myfield).addClass(textStatus);
						//$('#' + myfield).addClass('alert alert-error');
						$('#myAdjustmentModal').find('#' + myfield).parent().parent().addClass(textStatus);
						$('#myAdjustmentModal').find('#' + myfield).after('<span class="help_text error"> '+p[key]+'</span>');
					}
				}*/
		    },
		    
		  });
	});
			

$('#btnConfirmMeterReadUpdate').click(function(e){

		e.preventDefault();
		console.log("confirm update of Meter Read");
		$('.help_text').remove();
		//console.log("need to get acct number" + $(this).textContent);
		var now = new Date();
		console.log("now is "+ now.getMonth() + '/' + now.getDate() + '/' + now.getFullYear());
		var nowformat = now.getMonth() + '/' + now.getDate() + '/' + now.getFullYear()

		request = $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'POST',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/meters/updatemeterread/',
		    data: {'current_reading': $('#current-reading').val(),
		    	   'previous_reading': $('#previous-reading').val(),		    	    
		    	   'id': $('#id_meterread').val(),		    	    
				},
		    dataType: "json",
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Update Meter Read','success','',1500);
				
				$('#myUpdateMeterModal').modal('hide');
				window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Update Meter Read','fail','',1500);
		      	$('.control-group').removeClass('error');
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	/*var p = JSON.parse(request.responseText)
				for (var key in p) {
					if (p.hasOwnProperty(key)) {
						console.log('key and p key', key, p[key]);
						var myfield = 'id_' + key;
						console.log('myfield,', myfield);
						//$('.' + myfield).addClass(textStatus);
						//$('#' + myfield).addClass('alert alert-error');
						$('#myAdjustmentModal').find('#' + myfield).parent().parent().addClass(textStatus);
						$('#myAdjustmentModal').find('#' + myfield).after('<span class="help_text error"> '+p[key]+'</span>');
					}
				}*/
		    },
		    
		  });
	});



$('#btnConfirmCustomerUpdate').click(function(e){

		e.preventDefault();
		console.log("confirm update of Customer");
		$('.help_text').remove();
		//console.log("need to get acct number" + $(this).textContent);
		var now = new Date();
		console.log("now is "+ now.getMonth() + '/' + now.getDate() + '/' + now.getFullYear());
		var nowformat = now.getMonth() + '/' + now.getDate() + '/' + now.getFullYear()

		request = $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'POST',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/customers/updatecustomer/',
		    data: {'last_name': $('#last-name').val(),
		    	   'first_name': $('#first-name').val(),		    	    
		    	   'middle_name': $('#middle-name').val(),		    	    
		    	   'email_address': $('#email-address').val(),		    	    
		    	   'phone1': $('#phone1').val(),		    	    
		    	   'phone2': $('#phone2').val(),		    	    
		    	   'phone3': $('#phone3').val(),		    	    
		    	   'id': $('#id_customer').val(),		    	    
				},
		    dataType: "json",
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Update Customer','success','',1500);
				
				$('#myUpdateCustomerModal').modal('hide');
				window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Update Customer','fail','',1500);
		      	$('.control-group').removeClass('error');
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	/*var p = JSON.parse(request.responseText)
				for (var key in p) {
					if (p.hasOwnProperty(key)) {
						console.log('key and p key', key, p[key]);
						var myfield = 'id_' + key;
						console.log('myfield,', myfield);
						//$('.' + myfield).addClass(textStatus);
						//$('#' + myfield).addClass('alert alert-error');
						$('#myAdjustmentModal').find('#' + myfield).parent().parent().addClass(textStatus);
						$('#myAdjustmentModal').find('#' + myfield).after('<span class="help_text error"> '+p[key]+'</span>');
					}
				}*/
		    },
		    
		  });
	});
$('#btnAddMeter').click(function(e){

		e.preventDefault();
		console.log("Adding a New Meter");
		$('.help_text').remove();
		//console.log("need to get acct number" + $(this).textContent);
		var now = new Date();
		console.log("now is "+ now.getMonth() + '/' + now.getDate() + '/' + now.getFullYear());
		var nowformat = now.getMonth() + '/' + now.getDate() + '/' + now.getFullYear()

		request = $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'POST',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/meters/addnewmeter/',
		    data: {
		    		'current_reading': $('#id_meter_reading').val(),
		    		'new_meter': $('#id_new_meter').val(),
		    		'new_meter_reading': $('#id_new_reading').val(),
		    	   'account': $('#id_account').val(),		    	    
				},
		    dataType: "json",
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Add Meter','success','',1500);
				
				$('#myMeterModal').modal('hide');
				window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Add Meter','fail','',1500);
		      	$('.control-group').removeClass('error');
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	/*var p = JSON.parse(request.responseText)
				for (var key in p) {
					if (p.hasOwnProperty(key)) {
						console.log('key and p key', key, p[key]);
						var myfield = 'id_' + key;
						console.log('myfield,', myfield);
						//$('.' + myfield).addClass(textStatus);
						//$('#' + myfield).addClass('alert alert-error');
						$('#myAdjustmentModal').find('#' + myfield).parent().parent().addClass(textStatus);
						$('#myAdjustmentModal').find('#' + myfield).after('<span class="help_text error"> '+p[key]+'</span>');
					}
				}*/
		    },
		    
		  });
	});
	

$('#btnAddNote').click(function(e){

		e.preventDefault();
		console.log("Adding a New Note");
		$('.help_text').remove();
		//console.log("need to get acct number" + $(this).textContent);
		var now = new Date();
		console.log("now is "+ now.getMonth() + '/' + now.getDate() + '/' + now.getFullYear());
		var nowformat = now.getMonth() + '/' + now.getDate() + '/' + now.getFullYear()

		request = $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'POST',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/accounts/addnewnote/',
		    data: {
		    		'note': $('#id_note').val(),
		    	   'account': $('#id_account').val(),	
		    	   'user': $('#id_user').val(),
				},
		    dataType: "json",
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Add Note','success','',1500);
				
				$('#myNoteModal').modal('hide');
				window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Add Note','fail','',1500);
		      	$('.control-group').removeClass('error');
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	/*var p = JSON.parse(request.responseText)
				for (var key in p) {
					if (p.hasOwnProperty(key)) {
						console.log('key and p key', key, p[key]);
						var myfield = 'id_' + key;
						console.log('myfield,', myfield);
						//$('.' + myfield).addClass(textStatus);
						//$('#' + myfield).addClass('alert alert-error');
						$('#myAdjustmentModal').find('#' + myfield).parent().parent().addClass(textStatus);
						$('#myAdjustmentModal').find('#' + myfield).after('<span class="help_text error"> '+p[key]+'</span>');
					}
				}*/
		    },
		    
		  });
	});

	$('#alert_close').click(function(){
  		$('#alert_template').fadeOut('slow');
	});

	$('#id_type').change(function(){
		if ($('#id_type').val() === 'cash') {
			$('#id_check_number').prop('disabled',true);
			$('#id_check_number').val('')
		}
		else {
			$('#id_check_number').prop('disabled',false);
		}
	});

	$('#check_mode').change(function(){
		if ($('#check_mode').attr("checked") === "checked") {
			$('#id_check_number').prop('disabled',false);
			$('#posted_status').click();
			$('#posted_status').prop('disabled',true);

		}
	});
	$('#cash_mode').change(function(){
		if ($('#cash_mode').attr("checked") === "checked") {
			$('#id_check_number').prop('disabled',true);
			$('#posted_status').prop('disabled',false);
		}
	});

	$('#set_status_active').click(function(e){
		e.preventDefault();
		var account_id = $('#id_account').val();
		console.log('Setting Account ID '+ account_id + ' status to ACTIVE');

		$.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/accounts/setactive/' + account_id,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Set Account Status to ACTIVE','success',data['msg'],1500);
				window.setTimeout('location.reload()', 3000);
		    },
		    error: function(jqXHR, textStatus) {
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Set Account Status to ACTIVE','fail','',1500);
		      	},
		    dataType: "json"
		    });
	});

	$('#set_status_for_disconnection').click(function(e){
		e.preventDefault();
		var account_id = $('#id_account').val();
		console.log('Setting Account ID '+ account_id + ' status to FOR DISCONNECTION');

		$.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/accounts/setfordisconnection/' + account_id,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Set Account Status to FOR DISCONNECTION','success',data['msg'],1500);
				window.setTimeout('location.reload()', 3000);
		    },
		    error: function(jqXHR, textStatus) {
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Set Account Status to FOR DISCONNECTION','fail','',1500);
		      	},
		    dataType: "json"
		    });
	});

	$('#set_status_inactive').click(function(e){
		e.preventDefault();
		var account_id = $('#id_account').val();
		console.log('Setting Account ID '+ account_id + ' status to INACTIVE');

		$.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/accounts/setinactive/' + account_id,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Set Account Status to INACTIVE','success',data['msg'],1500);
				window.setTimeout('location.reload()', 3000);
		    },
		    error: function(jqXHR, textStatus) {
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Set Account Status to INACTIVE','fail','',1500);
		      	},
		    dataType: "json"
		    });
	});

	$('#set_status_disconnected').click(function(e){
		e.preventDefault();
		var account_id = $('#id_account').val();
		console.log('Setting Account ID '+ account_id + ' status to DISCONNECTED');

		$.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/accounts/setdisconnected/' + account_id,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Set Account Status to DISCONNECTED','success',data['msg'],1500);
				window.setTimeout('location.reload()', 3000);
		    },
		    error: function(jqXHR, textStatus) {
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Set Account Status to DISCONNECTED','fail','',1500);
		      	},
		    dataType: "json"
		    });
	});

	$('.btn-regeneratebill').click(function(e){
		e.preventDefault();
		account_id = $('#id_account').val();
		console.log('regenerate  bill button clicked: ' + account_id );
		 $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/bills/regeneratebill/' + account_id,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				if (data['regenerated']) {
					createAlertMessage('Bill Regeneration','success',data['msg'],5000);
					window.setTimeout('location.reload()', 5000);
				}
				else {
					createAlertMessage('Bill Regeneration','info',data['msg'],5000);
				}
				//$('#alert_template span').empty();
  				//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
				//$('#alert_template').addClass('alert-success');
				//$('#alert_template button').after('<span> ' + data['msg'] + ' </span>');
			
			
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	var data = JSON.parse(jqXHR.responseText)
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Bill Regeneration','fail',data['msg'],1500);
		      	//$('#alert_template span').empty();
		      	//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
  				//$('#alert_template').addClass('alert-error');
		      	//$('#alert_template button').after('<span> ' + textStatus['msg'] + ' </span>');
		      	$('.control-group').removeClass('error');
		      	//$('#myPaymentModal').modal('hide');
		      	//$('.control-group').addClass(textStatus);
		      	console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	
		    },
		    dataType: "json"
		  });
		
		//$('#myAdhocbillModal').modal('show');
	});



	$('.btn-adhocbill').click(function(e){
		e.preventDefault();
		account_id = $('#id_account').val();
		console.log('generate adhoc bill button clicked: ' + account_id );
		 $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/bills/generatebill/' + account_id,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				if (data['newly_created']) {
					createAlertMessage('Ad Hoc Bill Creation','success',data['msg'],5000);
					window.setTimeout('location.reload()', 5000);
				}
				else {
					createAlertMessage('Ad Hoc Bill Creation','info',data['msg'],5000);
				}
				//$('#alert_template span').empty();
  				//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
				//$('#alert_template').addClass('alert-success');
				//$('#alert_template button').after('<span> ' + data['msg'] + ' </span>');
				$('#myPaymentModal').modal('hide');
			
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	var data = JSON.parse(jqXHR.responseText)
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Ad Hoc Bill Creation','fail',data['msg'],1500);
		      	//$('#alert_template span').empty();
		      	//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
  				//$('#alert_template').addClass('alert-error');
		      	//$('#alert_template button').after('<span> ' + textStatus['msg'] + ' </span>');
		      	$('.control-group').removeClass('error');
		      	//$('#myPaymentModal').modal('hide');
		      	//$('.control-group').addClass(textStatus);
		      	console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	
		    },
		    dataType: "json"
		  });
		
		//$('#myAdhocbillModal').modal('show');
	});


	$('.btn-adhocnotice').click(function(e){
		e.preventDefault();
		account_id = $('#id_account').val();
		console.log('generate adhoc notice` button clicked: ' + account_id );
		 $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/notices/generatenotice/' + account_id,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				if (data['newly_created']) {
					createAlertMessage('Ad Hoc Notice Creation','success',data['msg'],1500);
				}
				else {
					createAlertMessage('Ad Hoc Notice Creation','info',data['msg'],1500);
				}
				//$('#alert_template span').empty();
  				//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
				//$('#alert_template').addClass('alert-success');
				//$('#alert_template button').after('<span> ' + data['msg'] + ' </span>');
				$('#myPaymentModal').modal('hide');
			window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	var data = JSON.parse(jqXHR.responseText)
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Ad Hoc Notice Creation','fail',data['msg'],1500);
		      	//$('#alert_template span').empty();
		      	//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
  				//$('#alert_template').addClass('alert-error');
		      	//$('#alert_template button').after('<span> ' + textStatus['msg'] + ' </span>');
		      	$('.control-group').removeClass('error');
		      	//$('#myPaymentModal').modal('hide');
		      	//$('.control-group').addClass(textStatus);
		      	console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	
		    },
		    dataType: "json"
		  });
		
		//$('#myAdhocbillModal').modal('show');
	});

	$('.btn-post').click(function(e){
		e.preventDefault();
		console.log('btn-post clicked');
		console.log('Payment id is ', $(this).parent().siblings()[2].textContent);
		payment_id = $(this).parent().siblings()[2].textContent;


		$.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/payments/post/' + payment_id,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Post Payment','success',data['msg'],1500);
				//$('#alert_template span').empty();
  				//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
				//$('#alert_template').addClass('alert-success');
				//$('#alert_template button').after('<span> ' + data['msg'] + ' </span>');
				$('#myPaymentModal').modal('hide');
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Post Payment','fail',textStatus['msg'],1500);
		      	//$('#alert_template span').empty();
		      	//$('#alert_template').removeClass('alert-error');
  				//$('#alert_template').removeClass('alert-success');
  				//$('#alert_template').fadeIn('slow');
  				//$('#alert_template').addClass('alert-error');
		      	//$('#alert_template button').after('<span> ' + textStatus['msg'] + ' </span>');
		      	$('.control-group').removeClass('error');
		      	//$('#myPaymentModal').modal('hide');
		      	//$('.control-group').addClass(textStatus);
		      	console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	var p = JSON.parse(jqXHR.responseText)
				for (var key in p) {
					if (p.hasOwnProperty(key)) {
						console.log('key and p key', key, p[key]);
						var myfield = 'id_' + key;
						console.log('myfield,', myfield);
						//$('.' + myfield).addClass(textStatus);
						//$('#' + myfield).addClass('alert alert-error');
						$('#' + myfield).parent().parent().addClass(textStatus);
						$('#' + myfield).after('<span class="help_text error"> '+p[key]+'</span>');


					}
				}
		    },
		    dataType: "json"
		  });
		window.setTimeout('location.reload()', 5000);

	});

	$('.btn-fail').click(function(e){
		e.preventDefault();
		console.log('btn-fail clicked');
		console.log('Payment id is ', $(this).parent().siblings()[2].textContent);
		payment_id = $(this).parent().siblings()[2].textContent;


		$.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/payments/fail/' + payment_id,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				$('#alert_template span').empty();
  				$('#alert_template').removeClass('alert-error');
  				$('#alert_template').removeClass('alert-success');
  				$('#alert_template').fadeIn('slow');
				$('#alert_template').addClass('alert-success');
				$('#alert_template button').after('<span> ' + data['msg'] + ' </span>');
				$('#myPaymentModal').modal('hide');
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	$('#alert_template span').empty();
		      	$('#alert_template').removeClass('alert-error');
  				$('#alert_template').removeClass('alert-success');
  				$('#alert_template').fadeIn('slow');
  				$('#alert_template').addClass('alert-error');
		      	$('#alert_template button').after('<span> ' + textStatus['msg'] + ' </span>');
		      	$('.control-group').removeClass('error');
		      	//$('#myPaymentModal').modal('hide');
		      	//$('.control-group').addClass(textStatus);
		      	console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	var p = JSON.parse(request.responseText)
				for (var key in p) {
					if (p.hasOwnProperty(key)) {
						console.log('key and p key', key, p[key]);
						var myfield = 'id_' + key;
						console.log('myfield,', myfield);
						//$('.' + myfield).addClass(textStatus);
						//$('#' + myfield).addClass('alert alert-error');
						$('#' + myfield).parent().parent().addClass(textStatus);
						$('#' + myfield).after('<span class="help_text error"> '+p[key]+'</span>');


					}
				}
		    },
		    dataType: "json"
		  });
		window.setTimeout('location.reload()', 5000);

	});

	$('#set_status_default').click(function(e){
		e.preventDefault();
		console.log('set status default clicked');
	});

	$('.reconnect-btn').click(function(e){
		e.preventDefault();
		console.log('reconnect clicked');
		var myid = $(this).parent().siblings()[0].childNodes[0].href.split("/")[4];
		console.log('myid',myid);
		//console.log('Account id is ', $(this).parent().siblings()[0].('a[href$*="/accounts/"]');
		$('#myaccid span').remove();
		$('#myaccid').append('<span>'+myid+'</span>');
		$('#id_account').val(myid);
		$('#myReconnectModal').modal('show');
	});

	$('.update-meterread-btn').click(function(e){
		e.preventDefault();
		console.log('update meter read clicked');
		var myid = $(this).parent().siblings()[0].childNodes[0].href.split("/")[4];
		console.log('myid',myid);
		//console.log('Meter id is ', $(this).parent().siblings()[0].('a[href$*="/accounts/"]');
		$('#mymreadid span').remove();
		$('#mymreadid').append('<span>'+myid+'</span>');
		$('#id_meterread').val(myid);
		$('#myUpdateMeterModal').modal('show');
	});

	$('#set-delinquent-fee').click(function(){
		myfee = $(this).val();
		console.log("myfee is "+myfee);
		$('#reconnection-fee').val(myfee);
		$('#set-remarks').val("delinquent");
	});

	$('#set-missed-fee').click(function(){
		myfee = $(this).val();
		console.log("myfee is "+myfee);
		$('#reconnection-fee').val(myfee);
		$('#set-remarks').val("missed");
	});

	$('#set-none-fee').click(function(){
		myfee = $(this).val();
		console.log("myfee is "+myfee);
		$('#reconnection-fee').val(myfee);
		$('#set-remarks').val("active");
	});
	
	//$('#bill_list').dataTable().fnSort([[2,'desc'],[0,'asc']]);

	function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}
$('#meter-read-upload').bind('fileuploadsubmit', function (e, data) {
    // The example input, doesn't have to be part of the upload form:
    var input = $('#input');
    seconds = new Date().getTime();
    data.formData = {'type':'meterread', 'pk':seconds};
    $('#myProgressModal').modal({backdrop:'static',keyboard:false});
	$('#myProgressModal').modal('show');
    
});


	$('#meter-read-upload').fileupload({
        url: '/meters/uploadreading/' ,
        dropZone: $('#meter-read-dropzone'),
        //formData: {'type':'meterread', 'pk':null},
        type: 'POST',
        dataType: 'json',
        crossDomain: false,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
            //alert("settings pk 2: "+ settings.formData.pk);
            //settings.formData = $.extend(settings.formData, {'pk': seconds});
  		    return true;
            //alert("settings: "+ settings.formData.pk);

        },
        done: function (e, data) {
            console.log("Upload done, got: " + JSON.stringify(data.result));
        },
        success: function (e, data) {
            console.log('e' + e);
            console.log('data' + data); 
            createAlertMessage('Meter Read Template Upload','success','',1500);
            window.setTimeout('location.reload()', 5000);
            },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#meter-read-progress .bar').css(
                'width',
                progress + '%'
            );
            var timeout = setTimeout(function(){
              $('#meter-read-progress .bar').css('width',0);
            }, 3000);
        },
        fail: function (e, data) {
          createAlertMessage('Meter Read upload ','fail','',5000);
        },
        singleFileUploads: true
    }).prop('disabled', !$.support.fileInput)	
		.parent().addClass($.support.fileInput ? undefined : 'disabled');

$('#btn-generatebills').click(function(e){
		e.preventDefault();
		console.log('generate bills button clicked: ');		
		seconds = new Date().getTime();
		//$('#myProgressModal').modal({backdrop:'static',keyboard:false});
		//$('#myProgressModal').modal('show');
				
		 $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/bills/generatebills/' + seconds,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				if (data['newly_created']) {
					
					createAlertMessage('Generate Bills','success',data['msg'],1500);
				}
				else {

					createAlertMessage('Generate Bills','info',data['msg'],1500);
				}
		      	console.log("Bills successfully generated!")	
		      	//window.location.replace('/tasks/');			
				window.setTimeout('location.reload()', 5000);
		    },

		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Generate Bills','fail','',1500);
		      	alert("Unable to generate bills!")
		      	console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	
		    },
		    dataType: "json"
		  });

		$('#myProgressModal').modal({backdrop:'static',keyboard:false});
		$('#myProgressModal').modal('show');
		 
	});


$('#myProgressModal').on('shown.bs.modal', function (e) {
  	console.log("seconds: "+ seconds);
  	drawszlider(100, 0);
  	window.status = 'in progress';
  	update();
  		
})

$('#btn-generatenotices').click(function(e){
		e.preventDefault();
		console.log('generate notices button clicked: ');
		seconds = new Date().getTime();

		 $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/notices/generatenotices/' + seconds,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Generate Notices','success',data['msg'],1500);
		      	console.log("Notices successfully generated!")
		      	//window.location.replace('/tasks/');			      		
				//window.setTimeout('location.reload()', 5000);
				window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Generate Notices','fail','',1500);
		      	console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	alert("Unable to generate notices")
		      	
		    },
		    dataTyspe: "json"
		  });
		$('#myProgressModal').modal({backdrop:'static',keyboard:false});
		$('#myProgressModal').modal('show');

	});


$('#btn-generatemasterlist').click(function(e){
		e.preventDefault();
		console.log('generate Master List button clicked: ');		
		$('#myWaitModal').modal({backdrop:'static',keyboard:false});
		$('#myWaitModal').modal('show');
				
		 $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/files/generatemasterlist/',
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
					
				createAlertMessage('Generate Master List','success',data['msg'],1500);
		      	console.log("Master List successfully generated!")
		      	$('#myWaitModal').modal('hide');	
		      	window.location= '/files/getmasterlist/';			
				//window.setTimeout('location.reload()', 5000);
		    },

		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Generate Master List','fail','',1500);
		      	alert("Unable to generate Master List!")
		      	console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	
		    },
		    dataType: "json"
		  });

		
		
		 
	});

function createAlertMessage(action,status,message,closeDelay) {
  //clear previous message and class
  console.log('Creating alert message: ' + action +'. ' + status + '. ' + message);
  $('#alert_template span').empty();
  $('#alert_template').removeClass('alert-error');
  $('#alert_template').removeClass('alert-success');
  $('#alert_template').removeClass('alert-info');
  $('#alert_template').fadeIn('slow');
  if (status === 'success') {
    $('#alert_template').addClass('alert-success');
    $('#alert_template button').after('<span>' + action + ' Successful. ' + message + '</span>');
    }
  else if (status === 'error') {
    $('#alert_template').addClass('alert-error');
    $('#alert_template button').after('<span>' + action + ' Failed. ' + message + '</span>');
    }
  else {
    $('#alert_template').addClass('info');
    $('#alert_template button').after('<span>' + action + ' Alert: ' + message + '</span>');
    }
  //$('#alert_template').delay(closeDelay).fadeOut('slow');
}

function setAccountStatusActive() {
	var account_id = $('#id_account').val();
	console.log('Setting Account ID '+ account_id + ' status to ACTIVE');
	
	$.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/accounts/setactive/' + account_id,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Set Account Status to ACTIVE','success',data['msg'],1500);
				window.setTimeout('location.reload()', 3000);
		    },
		    error: function(jqXHR, textStatus) {
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Set Account Status to ACTIVE','fail','',1500);
		      	},
		    dataType: "json"
		    });
}

// http://ruwix.com/simple-javascript-html-css-slider-progress-bar/
function drawszlider(ossz, meik){
	var szazalek=Math.round((meik*100)/ossz);
	document.getElementById("szliderbar").style.width=szazalek+'%';
	document.getElementById("szazalek").innerHTML=szazalek+'%';
	
}

function update(){
	//window.status = 'in progress';
 	total = 100;
  	actual = 0;
 
 	values = prepare(status);
 	console.log("---- winx : "+window.status);
 	console.log("---- VALUES : "+values.status);
 	//window.status = values.status;
 	total = values.jobs_total;
 	actual = values.jobs_done;
 	console.log("---- VALUES STATUS : "+values.status);
 	console.log("---- TOTAL: "+total);
 	console.log("---- VALUES TOTAL: "+values.jobs_total);
 	console.log("---- ACTUAL: "+actual);
 	console.log("---- VALUES ACTUAL: "+values.jobs_done);
  	drawszlider(total, actual);	

  	//alert('statuszzzz'+status);

	if (window.status !='in progress') {
		return;
	}
		
  	setTimeout(update, 1000);
  
}

function prepare() {
	
      	$.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/tasks/'+seconds,
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				//createAlertMessage('Get Task Info','success',data['msg'],1500);
				window.status = data['status'];
				window.jobs_total= data['jobs_total'];
				window.jobs_done = data['jobs_done'];
				//alert('status! ---xx: ' + window.status + " -- data: " + data['status']);
				//drawszlider(jobs_total, jobs_done);
		      	//window.location.replace('/tasks/');			      		
				//window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Get Task Info','fail','',1500);
		      	console.log("jqXHR",jqXHR);
		      	console.log("jqxhr response text",jqXHR.responseText);
		      	//status='completed';
		      	console.log("Unable to get task info");
		      	
		    },
		    dataType: "json"
		  });
	//alert('status!: ' + window.status);
	return {'status':window.status,'jobs_total':window.jobs_total, 'jobs_done':window.jobs_done};
}

})
