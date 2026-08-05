import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

public class TaskControllerTest {
    private TaskController controller;
    private TaskModel model;

    @Before
    public void setUp() {
        model = new TaskModel(); // предполагаем, что TaskModel - это класс модели
        controller = new TaskController(model); // предполагаем, что TaskController принимает модель в конструкторе
    }

    @Test
    public void testAddTask() {
        controller.addTask("Новая задача");
        assertEquals("Количество задач должно быть 1 после добавления задачи", 1, model.getTasks().size());
    }

    @Test
    public void testRemoveTask() {
        controller.addTask("Задача для удаления");
        controller.removeTask(0);
        assertTrue("Список задач должен быть пуст после удаления задачи", model.getTasks().isEmpty());
    }
}
