// $("button[name='btn_detail_event']").click(function() {
//
//     var data = { event_id : $(this).data('event_id')}
//
//     $.ajax({
//       type: 'POST',
//       url: "/detail_event",
//       data: data,
//       dataType: "text",
//       success: function(resultData) {
//           location.replace('/login');
//       }
// });
// });


$("button[name='btn_detail_event']").click(function() {

    window.location = "detail_event?event_id="+$(this).data('event_id');

});

$("button[name='btn_new_event']").click(function() {

    window.location = "new_event";

});



