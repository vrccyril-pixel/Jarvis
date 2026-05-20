import win32com.client
import datetime

def get_outlook_events():
    # Initialisation du client Outlook
    outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')

    # Récupération de l'agenda courant
    calendar = outlook.GetDefaultFolder(9)  # Le numéro 9 correspond à la folder 'Calendar'

    # Récupération des 5 prochains événements
    events = []
    for event in calendar.Items:
        if event.Class == 1:  # Événement (1 = Appointment, 2 = Meeting)
            events.append({
                'object': event.Subject,
                'start': event.Start,
                'duration': event.Duration
            })

    # Tri des événements par date de début
    events.sort(key=lambda x: x['start'])

    return events[:5]

def print_events(events):
    for event in events:
        print(f"Object: {event['object']}")
        print(f"Start: {event['start'].strftime('%Y-%m-%d %H:%M')}")
        print(f"Duration: {event['duration']} minutes")
        print()

events = get_outlook_events()
print_events(events)