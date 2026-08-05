import java.io.*;
import java.util.List;

public class TaskController {
    private TaskModel model;

    // Конструктор
    public TaskController(TaskModel model) {
        this.model = model;
    }

    // Добавление новой задачи
    public void addTask(String description) {
        if (description != null && !description.trim().isEmpty()) {
            model.addTask(description);
        }
    }

    // Удаление задачи по индексу
    public void removeTask(int index) {
        model.removeTask(index);
    }

    // Отметить задачу как выполненную
    public void completeTask(int index) {
        model.completeTask(index);
    }

    // Получение списка всех задач
    public List<Task> getTasks() {
        return model.getTasks();
    }

    // Сохранение текущего списка задач в файл
    public void saveTasksToFile(String filename) {
        try (ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(filename))) {
            out.writeObject(model.getTasks());
        } catch (IOException e) {
            // Обработка исключений при записи в файл
            e.printStackTrace();
        }
    }

    // Загрузка списка задач из файла
    public void loadTasksFromFile(String filename) {
        try (ObjectInputStream in = new ObjectInputStream(new FileInputStream(filename))) {
            List<Task> tasks = (List<Task>) in.readObject();
            model = new TaskModel(); // Создаем новую модель
            for (Task task : tasks) {
                model.addTask(task.getDescription());
                if (task.isCompleted()) {
                    model.completeTask(model.getTaskCount() - 1);
                }
            }
        } catch (IOException | ClassNotFoundException e) {
            // Обработка исключений при чтении из файла
            e.printStackTrace();
        }
    }
}
