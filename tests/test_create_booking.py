import requests
import pytest

BASE_URL = "https://restful-booker.herokuapp.com/booking"


@pytest.fixture
def default_booking_data():
    return {
        "firstname": "Alex",
        "lastname": "Brown",
        "totalprice": 128,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-09-01",
            "checkout": "2024-09-11"
        },
        "additionalneeds": "B&B"
    }


@pytest.mark.parametrize(
    "updates, expected_status_code",
    [
        ({}, 200),
        ({"additionalneeds": None}, 200),
        ({"firstname": "Jane", "lastname": "Smith", "totalprice": 111, "depositpaid": False}, 200),
        ({"totalprice": 99999999999}, 200),
        ({"totalprice": 0.99999999999999999999}, 200),
        ({"firstname": "", "lastname": "", "additionalneeds": ""}, 400),

        ({"depositpaid": None}, 400),
        ({"bookingdates": {"checkin": "2024-15-15"}}, 400),
        ({"bookingdates": {"checkin": "2024-09-11", "checkout": "2024-09-01"}}, 400),
        ({"bookingdates": {"checkin": "2024-09-11", "checkout": "2024-09-11"}}, 200),

        ({"firstname": 123}, 400),
        ({"totalprice": "111"}, 400),
        ({"depositpaid": "no"}, 400),

    ],
    ids=[
        "Default booking",
        "No additional needs",
        "Update all fields",
        "Large price value",
        "Small float price value",
        "Blank names and additional needs",  # TODO: report a bug, creates booking with empty firstname and lastname
        "Missing depositpaid field",
        "Invalid checkin date format",
        "Checkin later than checkout", # TODO: report a bug that checkout date should be later than checkin
        "Same checkin and checkout",  # TODO: verify requirements as returns 200
        "Invalid firstname data type",
        "Invalid totalprice data type",  # TODO: report a bug, totalprice is a number
        "Invalid depositpaid data type",  # TODO: report a critical bug, sets depositpais as true
    ]
)
def test_create_booking(default_booking_data, updates, expected_status_code):
    booking_data = {**default_booking_data, **updates}

    response = requests.post(BASE_URL, json=booking_data)

    assert response.status_code == expected_status_code, (
        f"Expected status code {expected_status_code}, but got {response.status_code}. "
        f"Response: {response.text}"
    )

    if response.status_code == 200:
        try:
            response_data = response.json()
        except ValueError:
            pytest.fail(f"Failed to decode JSON response: {response.content}")

        assert 'bookingid' in response_data, (
            f"Response does not contain 'bookingid'. Response: {response_data}"
        )
        assert 'booking' in response_data, (
            f"Response does not contain 'booking' field. Response: {response_data}"
        )

        booking_response = response_data['booking']

        assert booking_response["firstname"] == booking_data["firstname"], (
            f"Expected firstname '{booking_data['firstname']}', but got '{booking_response['firstname']}'"
        )
        assert booking_response["lastname"] == booking_data["lastname"], (
            f"Expected lastname '{booking_data['lastname']}', but got '{booking_response['lastname']}'"
        )
        assert booking_response["totalprice"] == booking_data["totalprice"], (
            f"Expected totalprice '{booking_data['totalprice']}', but got '{booking_response['totalprice']}'"
        )
        assert booking_response["depositpaid"] == booking_data["depositpaid"], (
            f"Expected depositpaid '{booking_data['depositpaid']}', but got '{booking_response['depositpaid']}'"
        )
        assert booking_response["bookingdates"]["checkin"] == booking_data["bookingdates"]["checkin"], (
            f"Expected checkin date '{booking_data['bookingdates']['checkin']}', but got '{booking_response['bookingdates']['checkin']}'"
        )
        assert booking_response["bookingdates"]["checkout"] == booking_data["bookingdates"]["checkout"], (
            f"Expected checkout date '{booking_data['bookingdates']['checkout']}', but got '{booking_response['bookingdates']['checkout']}'"
        )
        expected_additionalneeds = booking_data.get("additionalneeds", "")
        assert booking_response.get("additionalneeds") == expected_additionalneeds, (
            f"Expected additionalneeds '{expected_additionalneeds}', but got '{booking_response.get('additionalneeds')}'"
    )