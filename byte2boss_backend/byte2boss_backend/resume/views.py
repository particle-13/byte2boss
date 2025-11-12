from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import ResumeSerializer
from .models import Resume

class ResumeUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file_obj = request.FILES.get('resume')

        if not file_obj:
            return Response({"error": "No file uploaded"}, status=400)

        # Validate file type
        if not (file_obj.name.endswith(".pdf") or file_obj.name.endswith(".docx")):
            return Response({"error": "Only PDF or DOCX files are allowed"}, status=400)

        resume = Resume.objects.create(user=request.user, file=file_obj)
        serializer = ResumeSerializer(resume)
        return Response({
            "message": "Resume uploaded successfully",
            "resume": serializer.data
        }, status=201)
