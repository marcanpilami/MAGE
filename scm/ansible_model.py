from django.db import models




class Play(models.Model):
    name = models.CharField(max_length=100, verbose_name='play name')
    hosts = models.CharField(max_length=100, verbose_name='target')
    strategy = models.CharField(max_length=20, verbose_name='strategy', help_text='strategy de execution des taches dans cette play' )

    class Meta:
        verbose_name = 'play'
        verbose_name_plural = 'plays'
        
        
        
        
class Task(models.Model):
    
    name = models.CharField(max_length=100, verbose_name='task name')
    module_name = models.CharField(max_length=100, verbose_name='module name')
    delegate_to=models.CharField(max_length=100, verbose_name='delegation to another host')
    play = models.ForeignKey(Play,on_delete=models.CASCADE, related_name='tasks')
    

    class Meta:
        verbose_name = 'task'
        verbose_name_plural = 'tasks'
        
        
        
class Attribute(models.Model):
    
    attribute_name = models.CharField(max_length=100, verbose_name='task name')
    mannuel_value = models.CharField(max_length=100, verbose_name='mannuel field value ')
    automatique_value=models.CharField(max_length=100, verbose_name='automatic field value ')
    task = models.ForeignKey(Task,on_delete=models.CASCADE, related_name='attributes')
    
    

    class Meta:
        verbose_name = 'task'
        verbose_name_plural = 'tasks'        
        
