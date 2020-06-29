$("button[name='btn_delete_person']").click(function() {

    var data = { person_id : $(this).data('person_id')}

    $.ajax({
      type: 'POST',
      url: "/delete_person",
      data: data,
      dataType: "text",
      success: function(resultData) {
          location.replace('/login');
      }
});
});


$("button[name='btn_edit_person']").click(function() {

    window.location = "edit_person?person_id="+$(this).data('person_id');

});

