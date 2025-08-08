from django.shortcuts import render
import joblib
import pandas as pd
from datetime import timedelta
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.response import Response
from ..models import Transaction
import logging
import json
logging.basicConfig(level=logging.INFO)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _extract_and_validate_features(self, raw):
        required_fields = [
            "time_ind", "transac_type", "amount",
            "src_acc", "src_bal", "src_new_bal",
            "dst_acc", "dst_bal", "dst_new_bal",
            "is_flagged_fraud"
        ]
        missing = [f for f in required_fields if f not in raw]
        if missing:
            return None, Response({"error": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            time_ind = int(raw["time_ind"])
            amount = float(raw["amount"])
            src_bal = float(raw["src_bal"])
            src_new_bal = float(raw["src_new_bal"])
            dst_bal = float(raw.get("dst_bal") or 0)
            dst_new_bal = float(raw.get("dst_new_bal") or 0)
            transac_type = raw["transac_type"]
            start_date = pd.Timestamp("2025-01-01 00:00:00")
            time_ref = start_date + timedelta(hours=time_ind)
            dayofweek = time_ref.dayofweek
            week_of_month = ((time_ref.day - 1) // 7) + 1
            src_delta = src_new_bal - src_bal
            dst_delta = dst_new_bal - dst_bal
            transac_map = {
                "CASH_IN": 0.0,
                "CASH_OUT": 0.025833,
                "DEBIT": 0.0,
                "PAYMENT": 0.0,
                "TRANSFER": 0.0
            }
            if transac_type not in transac_map:
                return None, Response({"error": f"Invalid transac_type: {transac_type}"}, status=status.HTTP_400_BAD_REQUEST)
            transac_type_target = transac_map[transac_type]
            features = [
                week_of_month, dayofweek, time_ind,
                amount, src_delta, dst_delta, transac_type_target
            ]
            feature_names = [
                'week_of_month', 'dayofweek', 'time_ind',
                'amount', 'src_delta', 'dst_delta', 'transac_type_target'
            ]
            features_df = pd.DataFrame([features], columns=feature_names)
            return {
                "features_df": features_df,
                "time_ind": time_ind,
                "time_ref": time_ref,
                "transac_type": transac_type,
                "amount": amount,
                "src_acc": raw["src_acc"],
                "src_bal": src_bal,
                "src_new_bal": src_new_bal,
                "dst_acc": raw["dst_acc"],
                "dst_bal": dst_bal,
                "dst_new_bal": dst_new_bal,
                "is_flagged_fraud": raw.get("is_flagged_fraud"),
                "is_fraud": raw.get("is_fraud"),
                "raw": raw
            }, None
        except Exception as e:
            return None, Response({"error": f"Feature processing failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def _load_model(self):
        try:
            model = joblib.load('/Users/punnshelbo/Documents/GitHub/SCB/fraud_model.joblib')
            return model, None
        except Exception as e:
            return None, Response({"error": f"Failed to load model: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        raw = request.data.copy().get('raw_features', {})
        features, error = self._extract_and_validate_features(raw)
        if error:
            return error
        model, error = self._load_model()
        if error:
            return error
        try:
            prediction = bool(model.predict(features["features_df"])[0])
        except Exception as e:
            return Response({"error": f"Prediction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        transaction_data = {
            "time_ind": features["time_ind"],
            "time_ref": features["time_ref"],
            "transac_type": features["transac_type"],
            "amount": features["amount"],
            "src_acc": features["src_acc"],
            "src_bal": features["src_bal"],
            "src_new_bal": features["src_new_bal"],
            "dst_acc": features["dst_acc"],
            "dst_bal": features["dst_bal"],
            "dst_new_bal": features["dst_new_bal"],
            "is_flagged_fraud": features["is_flagged_fraud"],
            "is_fraud": features["is_fraud"],
            "prediction": prediction,
            "raw_features": features["raw"]
        }
        serializer = self.get_serializer(data=transaction_data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "prediction": prediction,
                "transaction_id": serializer.instance.id,
                "stored_transaction": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def upload_file(self, request, *args, **kwargs):
        ## this endpoint is used to perfrom file-based transaction prediction and store in the db
        file = request.FILES.get('csv_file')
        if not file:
            return Response({"error": "File is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return Response({"error": f"Failed to read CSV file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        if not all(col in df.columns for col in ["time_ind", "transac_type", "amount", "src_acc", "src_bal",
                                                         "src_new_bal", "dst_acc", "dst_bal", "dst_new_bal", "is_flagged_fraud"]):
                return Response({"error": f"Missing required columns in CSV file"}, status=status.HTTP_400_BAD_REQUEST)

        model, error = self._load_model()
        if error:
            return error

        for index, row in df.iterrows():
            raw = row.to_dict()
            features, error = self._extract_and_validate_features(raw)
            if error:
                return error
            try:
                prediction = bool(model.predict(features["features_df"])[0])
            except Exception as e:
                return Response({"error": f"Prediction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            transaction_data = {
                "time_ind": features["time_ind"],
                "time_ref": features["time_ref"],
                "transac_type": features["transac_type"],
                "amount": features["amount"],
                "src_acc": features["src_acc"],
                "src_bal": features["src_bal"],
                "src_new_bal": features["src_new_bal"],
                "dst_acc": features["dst_acc"],
                "dst_bal": features["dst_bal"],
                "dst_new_bal": features["dst_new_bal"],
                "is_flagged_fraud": features["is_flagged_fraud"],
                "is_fraud": features["is_fraud"],
                "prediction": prediction,
                "raw_features": features["raw"]
            }

            serializer = self.get_serializer(data=transaction_data)
            if serializer.is_valid():
                self.perform_create(serializer)
                log = {
                    "prediction": prediction,
                    "transaction_id": serializer.instance.id,
                    "stored_transaction": serializer.data
                }
                logging.info("%s", json.dumps(log, indent=4))

            elif serializer.errors:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "File processed successfully"}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        filters = {}
        # Build dynamic filter dict from query params
        for param, value in request.query_params.items():
            if param in [field.name for field in self.get_queryset().model._meta.get_fields()]:
                filters[param] = value

        queryset = self.get_queryset().filter(**filters)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def frauds(self, request, *args, **kwargs):
        # Assuming 'prediction' is a boolean field in the Transaction model
        queryset = self.get_queryset().filter(prediction=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)