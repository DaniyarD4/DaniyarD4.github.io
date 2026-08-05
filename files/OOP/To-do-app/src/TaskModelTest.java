import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

public class TaskModelTest {

    private TaskModel taskModel;

    @Before
    public void setUp() {
        taskModel = new TaskModel();
    }

    @Test
    public void testAddTask() {
        taskModel.addTask("Test task");
        assertEquals("Task count should be 1 after adding a task.", 1, taskModel.getTaskCount());
    }

    @Test
    public void testRemoveTask() {
        taskModel.addTask("Test task");
        taskModel.removeTask(0);
        assertEquals("Task count should be 0 after removing the task.", 0, taskModel.getTaskCount());
    }

    @Test
    public void testCompleteTask() {
        taskModel.addTask("Test task");
        taskModel.completeTask(0);
        assertTrue("Task should be marked as completed.", taskModel.getTasks().get(0).isCompleted());
    }

    @Test
    public void testGetRemainingTasks() {
        taskModel.addTask("Test task 1");
        taskModel.addTask("Test task 2");
        taskModel.completeTask(0);
        assertEquals("There should be 1 remaining task.", 1, taskModel.getRemainingTasks());
    }

    @Test
    public void testTaskDescription() {
        Task task = new Task("Test description");
        assertEquals("The description should match the one set in constructor.", "Test description", task.getDescription());
    }

    @Test
    public void testSetDescription() {
        Task task = new Task("Initial description");
        task.setDescription("Updated description");
        assertEquals("The description should be updated.", "Updated description", task.getDescription());
    }

    @Test
    public void testToString() {
        Task task = new Task("Test toString");
        assertEquals("toString should reflect the task is not completed.", "[ ] Test toString", task.toString());
        task.setCompleted(true);
        assertEquals("toString should reflect the task is completed.", "[X] Test toString", task.toString());
    }
}