
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

	$('.btn-payment').click(function(e){
		e.preventDefault();
		$('.control-group').removeClass('error');
		$('.help_text').remove();
		$('.controls').children().val('');
		$('#myPaymentModal').modal('show');
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
  				//$('#alert_template').fadeIn('slow');
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
		      	//$('#alert_template button').after('<span> Payment Failed. </span>');
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
		    	   'type': 'debit',
		    	   'description': $('#set-remarks').val(),
		    	   'account': $('#id_account').val(),
		    	   'adjustment_date': nowformat,
		    	    
				},
		    dataType: "json",
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Adjustment for Reconnection','success','',1500);
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
				createAlertMessage('Ad Hoc Bill Creation','success',data['msg'],1500);
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
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Ad Hoc Bill Creation','fail','',1500);
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


	$('#meter-read-upload').fileupload({
        url: '/meters/uploadreading/' ,
        dropZone: $('#meter-read-dropzone'),
        formData: {'type':'meterread',
                },
        type: 'POST',
        dataType: 'json',
        crossDomain: false,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        },
        done: function (e, data) {
            console.log("Upload done, got: " + JSON.stringify(data.result));
        },
        success: function (e, data) {
            console.log('e' + e);
            console.log('data' + data); 
            createAlertMessage('Meter Read Template Upload','success','',1500);
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
		 $.ajax({
			headers: {"X-CSRFToken":$.cookie('csrftoken')},
		    type: 'GET',
		    //contentType: "application/json; charset=utf-8", #commented since django empty POST data
		    url: '/bills/generatebill/',
		    success: function (data) {
				console.log("Got back: " + JSON.stringify(data));
				createAlertMessage('Generate Bills','success',data['msg'],1500);
				window.setTimeout('location.reload()', 5000);
		    },
		    error: function(jqXHR, textStatus) {
		      	//alert( "Request failed: " + textStatus );
		      	console.log("Got back: " + textStatus);
		      	createAlertMessage('Generate Bills','fail','',1500);
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
  $('#alert_template').fadeIn('slow');
  if (status === 'success') {
    $('#alert_template').addClass('alert-success');
    $('#alert_template button').after('<span>' + action + ' Successful. ' + message + '</span>');
    }
  else {
    $('#alert_template').addClass('alert-error');
    $('#alert_template button').after('<span>' + action + ' Failed. ' + message + '</span>');
    }
  $('#alert_template').delay(closeDelay).fadeOut('slow');
}

})
