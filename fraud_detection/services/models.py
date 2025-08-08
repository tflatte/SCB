from django.db import models

class Transaction(models.Model):
    # Extracted structured fields
    time_ind = models.IntegerField()
    time_ref = models.DateTimeField(null=True, blank=True)
    transac_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=30, decimal_places=6)
    src_acc = models.CharField(max_length=50)
    src_bal = models.DecimalField(max_digits=30, decimal_places=6)
    src_new_bal = models.DecimalField(max_digits=30, decimal_places=6)
    dst_acc = models.CharField(max_length=50, null=True, blank=True)
    dst_bal = models.DecimalField(max_digits=30, decimal_places=6, null=True, blank=True)
    dst_new_bal = models.DecimalField(max_digits=30, decimal_places=6, null=True, blank=True)

    is_fraud = models.BooleanField(null=True, blank=True)
    is_flagged_fraud = models.BooleanField(null=True, blank=True)

    prediction = models.BooleanField()

    raw_features = models.JSONField()

    status = models.BooleanField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.id} - {self.prediction}"


    class Meta:
        db_table = "transaction"
        indexes = [
            models.Index(fields=["prediction"]),
            models.Index(fields=["is_fraud"]),
            models.Index(fields=["transac_type"]),
        ]
