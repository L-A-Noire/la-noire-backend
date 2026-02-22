from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crime.models import Case, Complaint
from crime.permissions import IsCadet, IsPoliceOfficer
from crime.serializers import (
    ComplaintCreateSerializer,
    ComplaintDetailSerializer,
    ComplaintReviewSerializer,
    ComplaintSerializer,
    CrimeSerializer,
)


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return ComplaintCreateSerializer
        elif self.action in ["retrieve", "list"]:
            return ComplaintDetailSerializer
        return ComplaintSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.role:
            return Complaint.objects.none()

        role_title = user.role.title

        if role_title == "Administrator":
            return Complaint.objects.all()
        elif role_title == "Cadet":
            return Complaint.objects.filter(
                status__in=["pending_cadet", "rejected_by_cadet"], cadet=user
            )
        elif role_title == "Police/Patrol Officer":
            return Complaint.objects.filter(
                status="pending_officer", police_officer=user
            )
        elif role_title in ["Complainant", "Base User"]:
            return Complaint.objects.filter(complainants=user)
        else:
            return Complaint.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        complaint = serializer.save()

        return Response(
            ComplaintDetailSerializer(complaint).data,
            status=status.HTTP_201_CREATED,
        )


class ComplaintReviewByCadetView(generics.UpdateAPIView):
    queryset = Complaint.objects.filter(status="pending_cadet")
    serializer_class = ComplaintReviewSerializer
    permission_classes = [IsAuthenticated, IsCadet]

    def get_queryset(self):
        return self.queryset.filter(cadet=self.request.user)

    def update(self, request, *args, **kwargs):
        complaint = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_confirmed = serializer.validated_data["is_confirmed"]
        rejection_reason = serializer.validated_data.get("rejection_reason", "")

        if is_confirmed:
            complaint.status = "pending_officer"
            complaint.cadet_rejection_reason = "Null"
            message = "Complaint approved and forwarded to the police officer."
        else:
            complaint.status = "rejected_by_cadet"
            complaint.cadet_rejection_reason = rejection_reason
            complaint.rejection_count += 1

            if complaint.rejection_count >= 3:
                complaint.status = "invalid"
                message = (
                    "The complaint has been marked as invalid after three rejections."
                )
            else:
                message = "The complaint was rejected and returned to the complainant."

        complaint.save()

        return Response(
            {"message": message, "complaint": ComplaintDetailSerializer(complaint).data}
        )


class ComplaintReviewByOfficerView(generics.UpdateAPIView):
    queryset = Complaint.objects.filter(status="pending_officer")
    serializer_class = ComplaintReviewSerializer
    permission_classes = [IsAuthenticated, IsPoliceOfficer]

    def get_queryset(self):
        return self.queryset.filter(police_officer=self.request.user)

    def update(self, request, *args, **kwargs):
        complaint = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_confirmed = serializer.validated_data["is_confirmed"]
        rejection_reason = serializer.validated_data.get("rejection_reason", "")

        if is_confirmed:
            complaint.status = "approved"
            complaint.officer_rejection_reason = None
            message = "Complaint has been approved."
        else:
            complaint.status = "rejected_by_officer"
            complaint.officer_rejection_reason = rejection_reason

            from user.models import User

            new_cadet = (
                User.objects.filter(role__title="Cadet")
                .exclude(id=complaint.cadet.id)
                .first()
            )
            if new_cadet:
                complaint.cadet = new_cadet
                complaint.status = "pending_cadet"
                message = (
                    "Complaint rejected by officer and reassigned to another cadet."
                )
            else:
                message = (
                    "Complaint rejected by officer, but no alternative cadet was found."
                )

        complaint.save()

        return Response(
            {"message": message, "complaint": ComplaintDetailSerializer(complaint).data}
        )


class ComplaintCreateCaseView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsPoliceOfficer]

    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk, status="approved")

        if complaint.case:
            return Response(
                {"error": "A case has already been created for this complaint."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        crime_data = {
            "title": f"Complaint: {complaint.description[:50]}",
            "description": complaint.description,
            "level": "1",
            "committed_at": complaint.created_at,
            "location": "To be determined",
            "reported_by": request.user.id,
        }

        crime_serializer = CrimeSerializer(data=crime_data)
        if crime_serializer.is_valid():
            crime = crime_serializer.save()

            case = Case.objects.create(
                crime=crime, is_from_crime_scene=False, is_closed=False
            )

            complaint.case = case
            complaint.save()

            return Response(
                {
                    "message": "Case created successfully.",
                    "case_id": case.id,
                    "crime_id": crime.id,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(crime_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
