from datetime import datetime, timedelta

def generate_available_slots(schedule_start, schedule_end, service_duration, booked_slots, interval=5):
    """
    Genera slots disponibles según horario, duración de servicio y citas ya agendadas.
    
    schedule_start, schedule_end: datetime
    service_duration: int (minutos)
    booked_slots: list de tuples [(start_datetime, end_datetime), ...]
    interval: int (minutos entre servicios)
    """
    available_slots = []
    current_start = schedule_start

    while current_start + timedelta(minutes=service_duration) <= schedule_end:
        current_end = current_start + timedelta(minutes=service_duration)
        overlap = False

        for booked_start, booked_end in booked_slots:
            if not (current_end <= booked_start or current_start >= booked_end):
                overlap = True
                break

        if not overlap:
            available_slots.append((current_start, current_end))

        current_start = current_end + timedelta(minutes=interval)

    return available_slots
