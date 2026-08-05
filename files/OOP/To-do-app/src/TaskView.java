import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.List;

public class TaskView extends JFrame {
    private TaskController controller;
    private DefaultListModel<String> taskListModel;
    private JList<String> taskList;
    private JTextField newTaskField;
    private JButton addButton;
    private JButton removeButton;
    private JButton completeButton;
    private JButton saveButton;
    private JButton loadButton;

    // Конструктор
    public TaskView(TaskController controller) {
        this.controller = controller;
        initializeComponents();
        layoutComponents();
        initializeListeners();
        updateTaskList();
    }

    // Инициализация компонентов
    private void initializeComponents() {
        taskListModel = new DefaultListModel<>();
        taskList = new JList<>(taskListModel);
        newTaskField = new JTextField(20);
        addButton = new JButton("Add");
        removeButton = new JButton("Remove");
        completeButton = new JButton("Complete");
        saveButton = new JButton("Save");
        loadButton = new JButton("Load");
    }

    // Расположение компонентов на фрейме
    private void layoutComponents() {
        this.setLayout(new BorderLayout());
        this.add(new JScrollPane(taskList), BorderLayout.CENTER);

        JPanel inputPanel = new JPanel(new FlowLayout());
        inputPanel.add(newTaskField);
        inputPanel.add(addButton);
        inputPanel.add(removeButton);
        inputPanel.add(completeButton);
        inputPanel.add(saveButton);
        inputPanel.add(loadButton);
        this.add(inputPanel, BorderLayout.SOUTH);

        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        this.setTitle("Task Manager");
        this.pack();
        this.setVisible(true);
    }

    // Инициализация слушателей для кнопок и текстового поля
    private void initializeListeners() {
        addButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                controller.addTask(newTaskField.getText());
                newTaskField.setText("");
                updateTaskList();
            }
        });

        removeButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                int selectedIndex = taskList.getSelectedIndex();
                if (selectedIndex != -1) {
                    controller.removeTask(selectedIndex);
                    updateTaskList();
                }
            }
        });

        completeButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                int selectedIndex = taskList.getSelectedIndex();
                if (selectedIndex != -1) {
                    controller.completeTask(selectedIndex);
                    updateTaskList();
                }
            }
        });

        saveButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                controller.saveTasksToFile("tasks.dat");
            }
        });

        loadButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                controller.loadTasksFromFile("tasks.dat");
                updateTaskList();
            }
        });
    }

    // Обновление списка задач на экране
    private void updateTaskList() {
        List<Task> tasks = controller.getTasks();
        taskListModel.clear();
        for (Task task : tasks) {
            taskListModel.addElement(task.toString());
        }
    }
}