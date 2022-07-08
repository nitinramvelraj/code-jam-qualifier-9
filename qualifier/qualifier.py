import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """
        request_scope = request.scope
        if request_scope['type'] == 'staff.onduty':
            self.onboard_staff(request,request_scope)
        elif request_scope['type'] == 'staff.offduty':
            self.offboard_staff(request_scope)
        else:
            found = self.find_suitable_staff(request_scope)  # One selected member of staff
            full_order = await request.receive()
            await found.send(full_order)

            result = await found.receive()
            await request.send(result)
    
    def onboard_staff(self, request, request_scope):
        self.staff[request_scope['id']] = request
    
    def offboard_staff(self, request_scope):
        self.staff.pop(request_scope['id'], None)

    def convert_str_to_list(self, strng):
        return [strng]
        
    def find_suitable_staff(self, request_scope):
        request_speciality = request_scope['speciality']
        # base solution: iterate for every speciality in request 
        # through each staff. If staff has speciality then check 
        # for next until we find a spciality staff does not have
        # if we find a staff with all specialities then use that 
        # staff
        if isinstance(request_speciality, str):
            request_speciality = self.convert_str_to_list(request_speciality)
        
        selected_staff = None
        
        for staff in self.staff:
            staff_speciality_count = len(request_speciality)
            lst_staff_speciality = self.staff[staff].scope['speciality']
            if isinstance(lst_staff_speciality, str):
                lst_staff_speciality = self.convert_str_to_list(lst_staff_speciality)
            for speciality in request_speciality:
                if speciality not in lst_staff_speciality:
                    break
                else:
                    staff_speciality_count -= 1
            if staff_speciality_count == 0:
                selected_staff = staff
                return self.staff[selected_staff]
        return self.staff[staff]                