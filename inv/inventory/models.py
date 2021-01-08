import random

from django.db import models


class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    quantity = models.IntegerField(default=1)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


def add_stock():
    names = "The Holy Grail is traditionally thought to be the cup that Jesus Christ drank from at the Last Supper and that Joseph of Arimathea used to collect Jesus's blood at his crucifixion. From ancient legends to contemporary movies, the Holy Grail has been an object of mystery and fascination for centuries".split(" ")
    quantity = random.randint(1, 50)

    for x in range(1, 1000):
        Stock.objects.create(name=random.choice(names), quantity=quantity)

    return f"Done."