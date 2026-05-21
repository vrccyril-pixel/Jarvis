import datetime
import sys

def get_outlook_events():
    import win32com.client

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

def main() -> int:
    try:
        events = get_outlook_events()
    except ImportError as exc:
        print(
            f"Error: pywin32/win32com is required to read Outlook agenda: {exc}",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(f"Error: unable to read Outlook agenda: {exc}", file=sys.stderr)
        return 1

    print_events(events)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
