import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

// Класс задачи
public class Task implements Serializable {
    private String description;
    private boolean isCompleted;

    // Конструктор
    public Task(String description) {
        this.description = description;
        this.isCompleted = false;
    }

    // Геттер и сеттер для описания задачи
    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    // Геттер и сеттер для статуса задачи
    public boolean isCompleted() {
        return isCompleted;
    }

    public void setCompleted(boolean completed) {
        isCompleted = completed;
    }

    // Переопределение метода toString для удобного отображения задачи
    @Override
    public String toString() {
        return (isCompleted ? "[X] " : "[ ] ") + description;
    }
}

// Класс модели, содержащий список задач
class TaskModel implements Serializable {
    private List<Task> tasks;

    // Конструктор
    public TaskModel() {
        tasks = new ArrayList<>();
    }

    // Добавление новой задачи
    public void addTask(String description) {
        tasks.add(new Task(description));
    }

    // Удаление задачи
    public void removeTask(int index) {
        if(index >= 0 && index < tasks.size()) {
            tasks.remove(index);
        }
    }

    // Получение списка всех задач
    public List<Task> getTasks() {
        return tasks;
    }

    // Отметить задачу как выполненную
    public void completeTask(int index) {
        if(index >= 0 && index < tasks.size()) {
            tasks.get(index).setCompleted(true);
        }
    }

    // Получение количества задач
    public int getTaskCount() {
        return tasks.size();
    }

    // Получение количества невыполненных задач
    public int getRemainingTasks() {
        int count = 0;
        for(Task task : tasks) {
            if (!task.isCompleted()) {
                count++;
            }
        }
        return count;
    }
}
