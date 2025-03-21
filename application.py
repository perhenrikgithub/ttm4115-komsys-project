import stmpy

class Application:
    stm: stmpy.Machine 
    

    def __init__(self, username: str):
        self.username = username

    def reserve_scooter(self, scooter_id):
        print("reserve_scooter()")
        # publish to mqtt
        pass

    def unlock_scooter(self, scooter_id):
        print("unlock_scooter()")
        # publish to mqtt
        pass

    def park_scooter(self, scooter_id):
        print("park_scooter()")
        # publish to mqtt
        pass

    def calculate_bill(self, scooter_id):
        print("calculate_bill()")
        # publish to mqtt
        pass

    def complete_transaction(self, scooter_id):
        print("complete_transaction()")
        # publish to mqtt
        pass

    def file_report(self, scooter_id):
        print("file_report()")
        # publish to mqtt
        pass

application_states = [
    {
        'name': 'reserved',
        'entry': 'reserve_scooter'
    },
    {
        'name': 'driving',
        'entry': 'unlock_scooter'
    },
    {
        'name': 'park_scooter',
        'entry': 'park_scooter'
    },
    {
        'name': 'calculate_bill_and_pay',
        'entry': 'calculate_bill',
        'exit': 'complete_transaction'
    },
    {
        'name': 'idle',
    }
]

application_transitions = [
    {
        'source': 'initial',
        'target': 'idle'
    },
    {
        'source': 'idle',
        'target': 'reserved',
        'trigger': 'reserve'
    },
    {
        'source': 'reserved',
        'target': 'driving',
        'trigger': 'unlock'
    },
    {
        'source': 'idle',
        'target': 'driving',
        'trigger': 'unlock'
    },
    {
        'source': 'driving',
        'target': 'park_scooter',
        'trigger': 'park'
    },
    {
        'source': 'park_scooter',
        'target': 'calculate_bill_and_pay',
        'trigger': 'recive'
    },
    {
        'source': 'calculate_bill_and_pay',
        'target': 'idle',
        'trigger': 'pay'
    },
    {
        'source': 'idle',
        'target': 'idle',
        'trigger': 'report',
        'action': 'file_report'
    },
    {
        'source': 'reserved',
        'target': 'reserved',
        'trigger': 'report',
        'action': 'file_report'
    },
]

application = Application()
application_machine = stmpy.Machine(name=f'application', transitions=application_transitions, obj=application, states=application_states)
application.stm = application_machine

driver = stmpy.Driver()
driver.add_machine(application_machine)
driver.start()