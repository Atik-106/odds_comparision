from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_div(self):
        return 'd' + str(self.id)


class Competition(models.Model):
    name = models.CharField(max_length=255)
    com_id = models.IntegerField()
    game_name = models.ForeignKey(Game,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_div(self):
        return 'd' + str(self.id)


class Bookmarker(models.Model):
    BMID = models.IntegerField()
    name = models.CharField(max_length=333)

    def __str__(self):
        return self.name