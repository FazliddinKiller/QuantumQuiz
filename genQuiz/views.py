from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import os
import PyPDF2
import docx
from .models import Quiz
from generateQuiz.makeQuiz import generateQuiz

# Create your views here.
def home(request):
    login_form = AuthenticationForm()
    signup_form = UserCreationForm()
    context = {'login_form': login_form, 'signup_form': signup_form}
    return render(request, 'index.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('genQuiz:home')  # Redirect to the home page after login

    login_form = AuthenticationForm()
    signup_form = UserCreationForm()
    context = {'login_form': login_form, 'signup_form': signup_form}
    return render(request, 'index.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('genQuiz:home')  # Redirect to the home page after sign up

    login_form = AuthenticationForm()
    signup_form = UserCreationForm()
    context = {'login_form': login_form, 'signup_form': signup_form}
    return redirect('genQuiz:home')

def logout_view(request):
    logout(request)
    return redirect('genQuiz:home')

def genQuiz(request):
    return render(request, 'genQuiz.html')

@login_required
def profile(request):
    questions = Quiz.objects.filter(user=request.user).order_by('-created_at')
    context = {'quizzez': questions}
    return render(request, 'displayQuizzes.html', context)

@login_required
def generate(request):
    if request.method == 'POST':
        # Process the form data
        question_type = request.POST.get('questionType')
        context_type = request.POST.get('contextType')
        difficulty_level = request.POST.get('difficultyLevel')
        question_quantity = request.POST.get('quantity')
        document = [] # stores document type and destination

        data = { # stores all data from form
            'q_type':question_type,
            'con_type': context_type,
            'difficulty': difficulty_level,
            'quantity': question_quantity,
        }


        if context_type == 'document':
            uploaded_file = request.FILES['document']

            file_name = uploaded_file.name
            file_extension = file_name.split('.')[-1]  # Get file extension
            username = request.user.username # get username
            #Handle pdf file and save it
            if file_extension.lower() == 'pdf':
                # Get uploaded file and save it to a data/docs folder
                # Define the file path
                file_path = f'generateQuiz/type2text/data/docs/{username}.pdf'
                # Create the directory if it doesn't exist
                try:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    print('file created')
                except OSError as e:
                    print(f"Error creating directory: {e}")

                with open(f'generateQuiz/type2text/data/docs/{request.user.username}.pdf', 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                print('file written')
                with uploaded_file.open() as f:
                    reader = PyPDF2.PdfReader(f)
                    num_pages = len(reader.pages)               
                startPage = int(request.POST.get('startPage'))
                endPage = int(request.POST.get('endPage'))
                if startPage<1 or endPage>num_pages+1:
                    return JsonResponse({'message': 'Input Correct range of start and end numbers for the file!'})
                elif endPage - startPage<0:
                    return JsonResponse({'message': 'End number should be greater than start number!'})
                
                document = [file_extension, f'generateQuiz/type2text/data/docs/{username}.pdf', startPage, endPage+1]

                # Optionally, we can save information about the uploaded file in our database
            else:
                # Get uploaded file and save it to a data/docs folder
                # Define the file path
                file_path = f'generateQuiz/type2text/data/docs/{username}.docx'
                # Create the directory if it doesn't exist
                try:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                except OSError as e:
                    print(f"Error creating directory: {e}")
                # Get uploaded file and save it to a data/docs folder
                with open(f'generateQuiz/type2text/data/docs/{username}.docx', 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                doc = docx.Document(uploaded_file)
                num_pages = len(doc.paragraphs)

                startPage = int(request.POST.get('startPage'))
                endPage = int(request.POST.get('endPage'))

                if startPage<1 or endPage>num_pages:
                    return JsonResponse({'message': 'Input Correct range of start and end numbers for the file!'})
                elif endPage - startPage<0:
                    return JsonResponse({'message': 'End number should be greater than start number!'})
                
                document = [file_extension, f'generateQuiz/type2text/data/docs/{username}.docx', startPage-1, endPage]
            data['doc'] = document       
        elif context_type == 'url':
            url = request.POST.get('url')
            data['url'] = url
        else:
            text = request.POST.get('text')
            data['text'] = text
        
        questions = generateQuiz(data) # call this function to generate questions based on data
        print(questions)
        for quiz in questions:
            # Common fields for all question types
            common_fields = {
                'user': request.user,
                'question': quiz['question'],

            }
            print(data['q_type'])
            if data['q_type'] == 'MCQ':
                # Additional fields for multiple-choice questions
                data_model_instance = Quiz(
                    **common_fields,
                    answer= quiz['answer'],
                    option1=quiz['option1'],
                    option2=quiz['option2'],
                    option3=quiz['option3'],
                )
            elif data['q_type'] == 'True or False questions':
                # Additional fields for true/false questions
                data_model_instance = Quiz(
                    **common_fields,
                    option1=quiz['option1'],
                    option2=quiz['option2'],
                    answer= quiz['answer'],
                )
            else:
                # Additional fields for other question types
                data_model_instance = Quiz(
                    **common_fields,
                    option1=quiz['hint1'],
                    option2=quiz['hint2'],
                    option3=quiz['hint3'],
                    answer= quiz['answer'],
                )
            
            # Save the data model instance
            data_model_instance.save()

    return redirect('genQuiz:profile')
