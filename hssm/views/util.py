from datetime import datetime

from hssm.models.primary_models import Group, Class
from hssm.models.secondary_models import Client


def get_client(user):
    return user.client.get()


def current_adyear(get_list=False, year=1):
    #{datetime.now().year}-{str((datetime.now().year % 100) + 1)}

    now = datetime.now().year
    return [f"{i}-{(i % 100) + 1}" for i in range(now - 5, now + 5)] if get_list else f'2023-24'


def distribute_students(students, group: Group, no_of_classes: int, next_code: str, client: Client, year: int) -> str:
    class_gpa_sums = {v: 0 for v in range(no_of_classes)}
    new_classes = []
    for i in range(no_of_classes):
        new_classes.append(Class.objects.create(code=next_code, year=year, group=group, client=client))
        next_code = chr(ord(next_code) + 1)
    for student in students:
        index_of_new_class = min(class_gpa_sums, key=class_gpa_sums.get)
        student.AdClassNow = new_classes[index_of_new_class]
        student.save()
        class_gpa_sums[index_of_new_class] += student.index
        print(index_of_new_class, student, class_gpa_sums)

    return next_code
