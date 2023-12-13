from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Count

# Create your models here.
User = get_user_model()


class QuestionManager(models.Manager):
    def new_questions(self):
        return self.order_by('date').reverse()

    def hot_questions(self):
        return self.alias(c_rating=Count('rating')).order_by('-c_rating')

    def tag_questions(self, tag_id):
        return self.prefetch_related('tags').filter(tags__id=tag_id)

    def self_questions(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        return self.filter(author=profile)


class Question(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    head = models.CharField(max_length=256)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    rating = models.ManyToManyField('Rating', related_name='questions')
    tags = models.ManyToManyField('Tag', related_name='questions')

    def tags_list(self):
        return self.tags.all()

    def rating_count(self):
        return self.rating.count()

    def toggle_rating(self, profile_id):
        rating = self.rating.filter(profile_id=profile_id).first()
        if rating:
            rating.delete()
        else:
            rat = Rating.objects.create(profile_id=profile_id)
            self.rating.add(rat)

    def check_rating(self):
        profiles = []
        ratings = self.rating.all()
        for rating in ratings:
            profiles.append(rating.profile_id)
        return profiles

    def answers_count(self):
        return Answer.objects.one_question_answers_count(self.id)

    objects = QuestionManager()


class AnswerManager(models.Manager):
    def one_question_answers_count(self, question_id):
        return self.filter(question=question_id).count()

    def question_answers(self, question_id):
        return self.filter(question=question_id).all()

    def right_question_answers(self, question_id):
        return self.question_answers(question_id).order_by('correctness', 'date').reverse()

    def last_right_question_answers(self, question_id):
        return (self.question_answers(question_id).
                order_by('correctness', 'date').reverse().filter(correctness=True).last())


class Answer(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    rating = models.ManyToManyField('Rating', related_name='answers')
    correctness = models.BooleanField(default=False)

    def rating_count(self):
        return self.rating.count()

    def toggle_rating(self, profile_id):
        rating = self.rating.filter(profile_id=profile_id).first()
        if rating:
            rating.delete()
        else:
            rat = Rating.objects.create(profile_id=profile_id)
            self.rating.add(rat)

    def check_rating(self):
        profiles = []
        ratings = self.rating.all()
        for rating in ratings:
            profiles.append(rating.profile_id)
        return profiles

    objects = AnswerManager()


class Tag(models.Model):
    tag_name = models.CharField(max_length=256)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True,
                               default='default-avatar.png',
                               upload_to='uploads/%Y/%m/%d/')


class Rating(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
