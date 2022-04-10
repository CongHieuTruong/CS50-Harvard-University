(function () {
  'use strict'
  window.addEventListener(
    'load',
    function () {
      let forms = document.getElementsByClassName('needs-validation')
      Array.prototype.filter.call(forms, function (form) {
        form.addEventListener(
          'submit',
          function (event) {
            if (form.checkValidity() === false) {
              event.preventDefault()
              event.stopPropagation()
            }
            form.classList.add('was-validated')
          },
          false
        )
      })
    },
    false
  )
})()

$(document).on('submit', '#control_bid_field', function (e) {
  e.preventDefault()
  const auctionData = $(this).data('auction')
  const lastBidData = $(this).data('lastbid') == 'None' ? 0 : parseInt($(this).data('lastbid'))
  const startingBidData = parseInt($(this).data('startingbid'))
  const newBidUserInput = parseInt($('#newBid').val())
  let messageDisplayUser = $('#message')

  if (newBidUserInput > 0 && newBidUserInput > lastBidData && newBidUserInput > startingBidData) {
    $.ajax({
      type: 'POST',
      url: $(this).attr('action'),
      data: $(this).serialize(),
      success: function () {
        $(`.lastBid${auctionData}`).val(newBidUserInput)
        $(`.lastBid${auctionData}`).html(`Current Bid: ${newBidUserInput}`)
        $('#smallTotalBid').html(parseInt($('#smallTotalBid').html()) + 1)
        $('#yourLastBid').html('Congratulations, your bid is the current bid.')
        $('#newBid').val('')
        messageDisplayUser.attr('style',"font-size: 0;")
        // messageDisplayUser.remove()
      },
    })
  } else if (newBidUserInput === lastBidData || newBidUserInput === startingBidData) {
    messageDisplayUser.attr('style',"font-size: 80%;")
    messageDisplayUser.html('Your bid is equal with the current bid')
  } else {
    messageDisplayUser.attr('style',"font-size: 80%;")
    messageDisplayUser.html('Your bid is lower than the current bid, please place with the bigger than')
  }
})

$(document).on('submit', '#addItemToWatchList', function (e) {
    e.preventDefault()
    const watchListDisplayNumber = $('#button_heart_watchList')
    const watchListValue = watchListDisplayNumber.html()
  
    if ($('#button-auction').hasClass('added')) {
      $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        data: $(this).serialize(),
        success: function () {
          watchListDisplayNumber.text(parseInt(watchListValue) - 1)
          $('#heart').css('color', 'white')
          $('#button-auction').removeClass('added')
        },
      })
    } else {
      $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        data: $(this).serialize(),
        success: function () {
          watchListDisplayNumber.text(parseInt(watchListValue) + 1)
          $('#heart').css('color', 'red')
          $('#button-auction').addClass('added')
        },
      })
    }
    
})

$(document).on('submit', '#control_delete_comment', function (e) {
  e.preventDefault()
  const commentIdData = $(this).data('comment')
  const commentElement = $(`#comment${commentIdData}`)

  $.ajax({
    type: 'POST',
    url: $(this).attr('action'),
    data: $(this).serialize(),
    success: function () {
      commentElement.remove()
    },
  })
})

function removeEncryptionPassword(id, button) {

  const password = document.getElementById(id)
  const buttonJquery = document.getElementById(button)

  if (password.type === 'password') {
    password.type = 'text'
    buttonJquery.setAttribute('class', 'fa fa-eye-slash')
  } else {
    password.type = 'password'
    buttonJquery.setAttribute('class', 'fa fa-eye')
  }
}
