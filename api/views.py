from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import Teacher, Research
from .serializers import (
    TeacherSerializer,
    ResearchSerializer,
    RegisterSerializer,
    LoginSerializer,
    ClassSerializer,
    UserSerializer,
    SubjectSerializer
)
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Teacher, Class, ClassTeaching, UserRole, Subject, Exam, ExamResult
from django.utils.timezone import get_current_timezone

User = get_user_model()

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class ResearchViewSet(viewsets.ModelViewSet):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected endpoint!"})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TeacherClassesView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        # Get the authenticated teacher (User)
        teacher = request.user

        # Get the classes the teacher is teaching using ClassTeaching model
        classes = ClassTeaching.objects.filter(user=teacher)
        
        # Serialize the classes
        class_data = [class_taught.class_taught for class_taught in classes]
        serializer = ClassSerializer(class_data, many=True)

        # Create the response
        response = Response({"classes": serializer.data})

        # Add custom headers here
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'  # Add the Referrer-Policy header
        response['Custom-Header'] = 'Value'  # You can add other headers if needed

        # Return the response with custom headers
        return response
    
class ClassDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, pk):
        # Get the class object by primary key
        class_obj = get_object_or_404(Class, pk=pk)

        # Get the teachers associated with the class
        persons = ClassTeaching.objects.filter(class_taught=class_obj)

        subjects = Subject.objects.filter(class_assigned=class_obj)
        
        teachers = []
        students = []
        
        for person in persons:
            print(person.role)
            
            if person.role == UserRole.TEACHER:
                teachers.append(person.user)

            if person.role == UserRole.STUDENT:
                students.append(person.user)

        # Serialize teacher and student data
        teacher_serializer = UserSerializer(teachers, many=True)
        student_serializer = UserSerializer(students, many=True)
        subject_serializer = SubjectSerializer(subjects, many=True)

        # Serialize class data
        class_serializer = ClassSerializer(class_obj)

        # Return the class data with teachers and students
        return Response({
            'class': class_serializer.data,
            'teachers': teacher_serializer.data,
            'students': student_serializer.data,
            'subjects': subject_serializer.data
        })



class AddStudentToClass(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, class_id):
        # Get the class object
        class_obj = get_object_or_404(Class, id=class_id)

        # Check if the requesting user is a teacher in this class
        if not ClassTeaching.objects.filter(user=request.user, class_taught=class_obj, role=UserRole.TEACHER).exists():
            return Response({"error": "You are not authorized to add students to this class."}, status=status.HTTP_403_FORBIDDEN)

        # Get the student ID from request data
        student_id = request.data.get("student_id")
        if not student_id:
            return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the student object
        student = get_object_or_404(User, id=student_id)

        # Check if the user is already enrolled
        if ClassTeaching.objects.filter(user=student, class_taught=class_obj).exists():
            return Response({"error": "Student is already enrolled in this class."}, status=status.HTTP_400_BAD_REQUEST)

        # Enroll the student
        ClassTeaching.objects.create(user=student, class_taught=class_obj, role=UserRole.STUDENT)

        return Response({"message": "Student added successfully to the class."}, status=status.HTTP_201_CREATED)




class AddSubjectToClass(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, class_id):
        # Get the class object
        class_obj = get_object_or_404(Class, id=class_id)

        # Check if the user is a teacher in this class
        if not ClassTeaching.objects.filter(user=request.user, class_taught=class_obj, role=UserRole.TEACHER).exists():
            return Response({"error": "You are not authorized to add subjects to this class."}, status=status.HTTP_403_FORBIDDEN)

        # Get the subject data from the request
        subject_name = request.data.get("name")
        subject_description = request.data.get("description", "")

        # Validate subject name
        if not subject_name:
            return Response({"error": "Subject name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new subject and associate it with the class
        subject = Subject.objects.create(
            name=subject_name,
            description=subject_description,
            class_assigned=class_obj
        )

        return Response({
            "message": "Subject added successfully to the class.",
            "subject": {
                "name": subject.name,
                "description": subject.description
            }
        }, status=status.HTTP_201_CREATED)



class CreateExamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, class_id, subject_id):
        # Get the class and subject objects
        class_obj = get_object_or_404(Class, id=class_id)
        subject_obj = get_object_or_404(Subject, id=subject_id)

        # Check if the user is a teacher for the specified class
        if not ClassTeaching.objects.filter(user=request.user, class_taught=class_obj, role=UserRole.TEACHER).exists():
            return Response({"error": "You are not authorized to create an exam for this class."}, status=status.HTTP_403_FORBIDDEN)

        # Get the exam details from the request
        exam_name = request.data.get("name")
        exam_description = request.data.get("description", "")

        # Validate input
        if not exam_name:
            return Response({"error": "Exam name and date are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the exam date into a datetime object

        exam = Exam.objects.create(
            name=exam_name,
            description=exam_description,
            class_assigned=class_obj,
            subject=subject_obj
        )

        return Response({
            "message": "Exam created successfully.",
            "exam": {
                "name": exam.name,
                "description": exam.description,
            }
        }, status=status.HTTP_201_CREATED)



class PublishExamResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exam_id):
        # Get the exam object
        exam = get_object_or_404(Exam, id=exam_id)

        # Check if the user is a teacher for this class
        if not exam.class_assigned.teachers.filter(id=request.user.id).exists():
            return Response({"error": "You are not authorized to publish results for this exam."}, status=status.HTTP_403_FORBIDDEN)

        # Get the results data from the request
        results_data = request.data.get("results")
        if not results_data:
            return Response({"error": "No results data provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update the ExamResult for this exam
        exam_result, created = ExamResult.objects.get_or_create(Exam=exam)

        # Loop through the results and add them to the ExamResult model
        for result in results_data:
            student_id = result.get("student_id")
            marks = result.get("marks")
            grade = result.get("grade", None)

            # Ensure the student exists
            student = get_object_or_404(User, id=student_id)

            # Add the student result to the exam results (in JSON format)
            exam_result.add_student_result(student, marks, grade)

        return Response({"message": "Exam results published successfully!"}, status=status.HTTP_201_CREATED)



class ViewExamResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        # Get the exam result for the provided exam ID
        exam_result = get_object_or_404(ExamResult, Exam__id=exam_id)

        # Retrieve the results from the JSONField
        results = exam_result.results

        # If there are no results, return a message indicating so
        if not results:
            return Response({"message": "No results published for this exam yet."}, status=status.HTTP_404_NOT_FOUND)

        # Return the results in the response
        return Response({
            "exam": exam_result.Exam.name,
            "subject": exam_result.Exam.subject.name,
            "results": results
        }, status=status.HTTP_200_OK)