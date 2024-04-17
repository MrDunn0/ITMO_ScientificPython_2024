import openmeteo_requests
from datetime import datetime


class IncreaseSpeed:

    def __init__(self, current_speed: int, max_speed: int, step: int = 10) -> None:
        self.current_speed = current_speed
        self.max_speed = max_speed
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        speed = self.current_speed + self.step
        if speed > self.max_speed:
            speed = self.max_speed
        self.current_speed = speed
        return speed


class DecreaseSpeed:
    def __init__(self, current_speed: int, step: int = 10) -> None:
        self.current_speed = current_speed
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        speed = self.current_speed - self.step
        if speed < 0:
            speed = 0
        self.current_speed = speed
        return speed


class Car:

    _cars_on_the_road = 0

    def __init__(self, max_speed: int, state: str, current_speed: int = 0):
        self.state = state
        self.max_speed = max_speed
        self.current_speed = current_speed
        if self.state == 'on the road':
            Car._cars_on_the_road += 1

    def accelerate(self, upper_border=None):

        if self.state == 'on the road':
            speed_limit = self.max_speed if upper_border is None else upper_border
            up_iterator = IncreaseSpeed(
                self.current_speed, speed_limit)

            if upper_border is None:
                speed = next(up_iterator)
                if speed > self.current_speed:
                    print(f'Speed increased from {self.current_speed} to {speed}')
                    self.current_speed = speed

            elif upper_border >= 0 and upper_border <= self.max_speed:
                for speed in up_iterator:
                    if self.current_speed == upper_border:
                        break
                    print(f'Speed increased from {self.current_speed} to {speed}')
                    self.current_speed = speed

            else:
                raise ValueError(
                    f'Upper border value must be between 0 and {self.max_speed}\n' +
                    f'Your value: {upper_border}')

        else:
            print('Leaving the parking is not implemented. You will stay here forever!')

    def brake(self, lower_border=None):

        down_iterator = DecreaseSpeed(self.current_speed)

        if lower_border is None:
            speed = next(down_iterator)
            if speed < self.current_speed:
                print(f'Speed decreased from {self.current_speed} to {speed}')
                self.current_speed = speed

        elif lower_border >= 0 and lower_border <= self.current_speed:
            for speed in down_iterator:
                if self.current_speed == lower_border:
                    break
                print(f'Speed decreased from {self.current_speed} to {speed}')
                self.current_speed = speed
        else:
            raise ValueError(
                f'Lower border value must be between 0 and {self.current_speed}\n' +
                f'Your value: {lower_border}')

    def parking(self):
        if self.state == 'on the road':
            self.state = 'in the parking'
            Car._cars_on_the_road -= 1
        else:
            print('Already in the parking')

    @classmethod
    def total_cars(cls):
        print(f'Cars on the road: {cls._cars_on_the_road}')

    @staticmethod
    def show_weather():
        openmeteo = openmeteo_requests.Client()
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 59.9386, # for St.Petersburg
            "longitude": 30.3141, # for St.Petersburg
            "current": ["temperature_2m", "apparent_temperature", "rain", "wind_speed_10m"],
            "wind_speed_unit": "ms",
            "timezone": "Europe/Moscow"
        }
        response = openmeteo.weather_api(url, params=params)[0]
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_apparent_temperature = current.Variables(1).Value()
        current_rain = current.Variables(2).Value()
        current_wind_speed_10m = current.Variables(3).Value()

        print(f"Current time: {datetime.fromtimestamp(current.Time())} {response.TimezoneAbbreviation().decode()}")
        print(f"Current temperature: {round(current_temperature_2m, 0)} C")
        print(f"Current apparent_temperature: {round(current_apparent_temperature, 0)} C")
        print(f"Current rain: {current_rain} mm")
        print(f"Current wind_speed: {round(current_wind_speed_10m, 1)} m/s")


if __name__ == '__main__':

    Car.total_cars()
    car_1 = Car(100, 'on the road', current_speed=0)
    car_2 = Car(220, 'in the parking')
    Car.total_cars()
    car_1.accelerate(100)
    car_1.brake(60)
    print()
    car_1.brake()
    print()
    car_1.brake(0)
    car_1.brake()
    car_1.show_weather()
    car_1.parking()
    Car.total_cars()
    car_2.parking()
    car_2.accelerate()
    car_2.brake()
