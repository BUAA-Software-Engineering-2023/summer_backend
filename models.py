from django.db import models

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super(SoftDeleteQuerySet, self).update(is_deleted=True)

    def hard_delete(self):
        return super(SoftDeleteQuerySet, self).delete()

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model).filter(is_deleted=False)

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    objects = SoftDeleteManager()
    objects_all = models.Manager()

    class Meta:
        abstract = True