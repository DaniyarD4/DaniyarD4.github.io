public class Main {
    public static void main(String[] args) {
        // Создание модели
        TaskModel model = new TaskModel();

        // Создание контроллера и связывание его с моделью
        TaskController controller = new TaskController(model);

        // Запуск графического интерфейса пользователя в потоке обработки событий
        javax.swing.SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                // Создание представления и связывание его с контроллером
                TaskView view = new TaskView(controller);

                // Отображение пользовательского интерфейса
                view.setVisible(true);
            }
        });
    }
}