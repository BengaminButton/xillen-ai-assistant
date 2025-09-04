package xillenaiassistant;

import java.util.*;
import java.time.*;
import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.concurrent.*;
import java.util.regex.*;

public class Main {
    private static final String author = "t.me/Bengamin_Button t.me/XillenAdapter";
    private static final Scanner scanner = new Scanner(System.in);
    private static final Map<String, String> memory = new HashMap<>();
    private static final List<String> history = new ArrayList<>();
    private static final ExecutorService executor = Executors.newFixedThreadPool(4);
    private static boolean running = true;
    
    public static void main(String[] args) {
        System.out.println(author);
        System.out.println("=== XILLEN AI ASSISTANT ===");
        System.out.println("Введите 'help' для списка команд или 'exit' для выхода");
        
        loadMemory();
        startBackgroundTasks();
        
        while (running) {
            System.out.print("\n> ");
            String input = scanner.nextLine().trim();
            
            if (input.isEmpty()) continue;
            
            history.add(input);
            processCommand(input);
        }
        
        saveMemory();
        executor.shutdown();
        System.out.println("До свидания!");
    }
    
    private static void processCommand(String input) {
        String[] parts = input.toLowerCase().split("\\s+");
        String command = parts[0];
        
        switch (command) {
            case "exit":
            case "выход":
                running = false;
                break;
                
            case "help":
            case "помощь":
                showHelp();
                break;
                
            case "time":
            case "время":
                showTime();
                break;
                
            case "date":
            case "дата":
                showDate();
                break;
                
            case "random":
            case "случайное":
                generateRandom(parts);
                break;
                
            case "calc":
            case "вычислить":
                calculate(parts);
                break;
                
            case "remember":
            case "запомнить":
                remember(parts);
                break;
                
            case "recall":
            case "вспомнить":
                recall(parts);
                break;
                
            case "weather":
            case "погода":
                getWeather(parts);
                break;
                
            case "translate":
            case "перевести":
                translate(parts);
                break;
                
            case "file":
            case "файл":
                fileOperations(parts);
                break;
                
            case "network":
            case "сеть":
                networkOperations(parts);
                break;
                
            case "system":
            case "система":
                systemInfo();
                break;
                
            case "history":
            case "история":
                showHistory();
                break;
                
            case "clear":
            case "очистить":
                clearScreen();
                break;
                
            case "joke":
            case "шутка":
                tellJoke();
                break;
                
            case "quote":
            case "цитата":
                showQuote();
                break;
                
            default:
                handleNaturalLanguage(input);
                break;
        }
    }
    
    private static void showHelp() {
        System.out.println("\n=== ДОСТУПНЫЕ КОМАНДЫ ===");
        System.out.println("time/время - показать текущее время");
        System.out.println("date/дата - показать текущую дату");
        System.out.println("random/случайное [min] [max] - случайное число");
        System.out.println("calc/вычислить <выражение> - вычислить математическое выражение");
        System.out.println("remember/запомнить <ключ> <значение> - запомнить информацию");
        System.out.println("recall/вспомнить <ключ> - вспомнить информацию");
        System.out.println("weather/погода [город] - информация о погоде");
        System.out.println("translate/перевести <текст> - перевод текста");
        System.out.println("file/файл <операция> <путь> - операции с файлами");
        System.out.println("network/сеть <операция> - сетевые операции");
        System.out.println("system/система - информация о системе");
        System.out.println("history/история - показать историю команд");
        System.out.println("clear/очистить - очистить экран");
        System.out.println("joke/шутка - рассказать шутку");
        System.out.println("quote/цитата - показать цитату");
        System.out.println("exit/выход - выход из программы");
    }
    
    private static void showTime() {
        LocalTime now = LocalTime.now();
        System.out.println("Текущее время: " + now.format(java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss")));
    }
    
    private static void showDate() {
        LocalDate now = LocalDate.now();
        System.out.println("Сегодня: " + now.format(java.time.format.DateTimeFormatter.ofPattern("dd.MM.yyyy")));
    }
    
    private static void generateRandom(String[] parts) {
        int min = 1, max = 100;
        if (parts.length > 1) min = Integer.parseInt(parts[1]);
        if (parts.length > 2) max = Integer.parseInt(parts[2]);
        
        Random rand = new Random();
        int result = rand.nextInt(max - min + 1) + min;
        System.out.println("Случайное число: " + result);
    }
    
    private static void calculate(String[] parts) {
        if (parts.length < 2) {
            System.out.println("Использование: calc <выражение>");
            return;
        }
        
        try {
            String expression = String.join(" ", Arrays.copyOfRange(parts, 1, parts.length));
            double result = evaluateExpression(expression);
            System.out.println("Результат: " + result);
        } catch (Exception e) {
            System.out.println("Ошибка вычисления: " + e.getMessage());
        }
    }
    
    private static double evaluateExpression(String expr) {
        expr = expr.replaceAll("\\s+", "");
        return new Object() {
            int pos = -1, ch;
            
            void nextChar() {
                ch = (++pos < expr.length()) ? expr.charAt(pos) : -1;
            }
            
            boolean eat(int charToEat) {
                while (ch == ' ') nextChar();
                if (ch == charToEat) {
                    nextChar();
                    return true;
                }
                return false;
            }
            
            double parse() {
                nextChar();
                double x = parseExpression();
                if (pos < expr.length()) throw new RuntimeException("Unexpected: " + (char)ch);
                return x;
            }
            
            double parseExpression() {
                double x = parseTerm();
                for (;;) {
                    if (eat('+')) x += parseTerm();
                    else if (eat('-')) x -= parseTerm();
                    else return x;
                }
            }
            
            double parseTerm() {
                double x = parseFactor();
                for (;;) {
                    if (eat('*')) x *= parseFactor();
                    else if (eat('/')) x /= parseFactor();
                    else return x;
                }
            }
            
            double parseFactor() {
                if (eat('+')) return parseFactor();
                if (eat('-')) return -parseFactor();
                
                double x;
                int startPos = this.pos;
                if (eat('(')) {
                    x = parseExpression();
                    eat(')');
                } else if ((ch >= '0' && ch <= '9') || ch == '.') {
                    while ((ch >= '0' && ch <= '9') || ch == '.') nextChar();
                    x = Double.parseDouble(expr.substring(startPos, this.pos));
                } else {
                    throw new RuntimeException("Unexpected: " + (char)ch);
                }
                
                if (eat('^')) x = Math.pow(x, parseFactor());
                
                return x;
            }
        }.parse();
    }
    
    private static void remember(String[] parts) {
        if (parts.length < 3) {
            System.out.println("Использование: remember <ключ> <значение>");
            return;
        }
        
        String key = parts[1];
        String value = String.join(" ", Arrays.copyOfRange(parts, 2, parts.length));
        memory.put(key, value);
        System.out.println("Запомнил: " + key + " = " + value);
    }
    
    private static void recall(String[] parts) {
        if (parts.length < 2) {
            System.out.println("Использование: recall <ключ>");
            return;
        }
        
        String key = parts[1];
        String value = memory.get(key);
        if (value != null) {
            System.out.println(key + ": " + value);
        } else {
            System.out.println("Не помню: " + key);
        }
    }
    
    private static void getWeather(String[] parts) {
        String city = (parts.length > 1) ? parts[1] : "Москва";
        System.out.println("Погода в " + city + ":");
        System.out.println("Температура: " + (new Random().nextInt(30) - 10) + "°C");
        System.out.println("Влажность: " + (new Random().nextInt(40) + 40) + "%");
        System.out.println("Ветер: " + (new Random().nextInt(20)) + " м/с");
    }
    
    private static void translate(String[] parts) {
        if (parts.length < 2) {
            System.out.println("Использование: translate <текст>");
            return;
        }
        
        String text = String.join(" ", Arrays.copyOfRange(parts, 1, parts.length));
        System.out.println("Перевод: " + text + " (симуляция перевода)");
    }
    
    private static void fileOperations(String[] parts) {
        if (parts.length < 3) {
            System.out.println("Использование: file <операция> <путь>");
            System.out.println("Операции: read, write, list, delete");
            return;
        }
        
        String operation = parts[1];
        String path = parts[2];
        
        try {
            switch (operation) {
                case "read":
                    String content = Files.readString(Paths.get(path));
                    System.out.println("Содержимое файла:\n" + content);
                    break;
                case "write":
                    System.out.print("Введите текст для записи: ");
                    String text = scanner.nextLine();
                    Files.writeString(Paths.get(path), text);
                    System.out.println("Файл записан");
                    break;
                case "list":
                    Files.list(Paths.get(path)).forEach(p -> System.out.println(p.getFileName()));
                    break;
                case "delete":
                    Files.delete(Paths.get(path));
                    System.out.println("Файл удалён");
                    break;
                default:
                    System.out.println("Неизвестная операция");
            }
        } catch (Exception e) {
            System.out.println("Ошибка: " + e.getMessage());
        }
    }
    
    private static void networkOperations(String[] parts) {
        if (parts.length < 2) {
            System.out.println("Использование: network <операция>");
            System.out.println("Операции: ping, scan, info");
            return;
        }
        
        String operation = parts[1];
        
        switch (operation) {
            case "ping":
                System.out.print("Введите адрес для ping: ");
                String address = scanner.nextLine();
                System.out.println("Ping " + address + " (симуляция)");
                break;
            case "scan":
                System.out.println("Сканирование портов (симуляция)");
                break;
            case "info":
                try {
                    InetAddress localhost = InetAddress.getLocalHost();
                    System.out.println("IP адрес: " + localhost.getHostAddress());
                    System.out.println("Имя хоста: " + localhost.getHostName());
                } catch (Exception e) {
                    System.out.println("Ошибка получения сетевой информации");
                }
                break;
            default:
                System.out.println("Неизвестная операция");
        }
    }
    
    private static void systemInfo() {
        Runtime runtime = Runtime.getRuntime();
        System.out.println("=== ИНФОРМАЦИЯ О СИСТЕМЕ ===");
        System.out.println("OS: " + System.getProperty("os.name"));
        System.out.println("Версия: " + System.getProperty("os.version"));
        System.out.println("Архитектура: " + System.getProperty("os.arch"));
        System.out.println("Java версия: " + System.getProperty("java.version"));
        System.out.println("Пользователь: " + System.getProperty("user.name"));
        System.out.println("Домашняя директория: " + System.getProperty("user.home"));
        System.out.println("Рабочая директория: " + System.getProperty("user.dir"));
        System.out.println("Доступная память: " + (runtime.freeMemory() / 1024 / 1024) + " MB");
        System.out.println("Максимальная память: " + (runtime.maxMemory() / 1024 / 1024) + " MB");
        System.out.println("Общая память: " + (runtime.totalMemory() / 1024 / 1024) + " MB");
    }
    
    private static void showHistory() {
        System.out.println("\n=== ИСТОРИЯ КОМАНД ===");
        for (int i = 0; i < history.size(); i++) {
            System.out.println((i + 1) + ". " + history.get(i));
        }
    }
    
    private static void clearScreen() {
        System.out.print("\033[H\033[2J");
        System.out.flush();
    }
    
    private static void tellJoke() {
        String[] jokes = {
            "Почему программисты не любят природу? Потому что в ней слишком много багов!",
            "Что общего у программиста и волшебника? Оба работают с магией, но только один понимает, что делает.",
            "Почему Java разработчики носят очки? Потому что не могут C#!",
            "Сколько программистов нужно, чтобы вкрутить лампочку? Ни одного, это аппаратная проблема!",
            "Почему Python не может летать? Потому что у него нет крыльев, только змеи!"
        };
        
        Random rand = new Random();
        System.out.println(jokes[rand.nextInt(jokes.length)]);
    }
    
    private static void showQuote() {
        String[] quotes = {
            "Код — это поэзия, которая исполняется.",
            "Программирование — это искусство решения проблем.",
            "Хороший код — это код, который легко читать и понимать.",
            "Ошибки — это не баги, это особенности.",
            "Программист — это человек, который превращает кофе в код."
        };
        
        Random rand = new Random();
        System.out.println(quotes[rand.nextInt(quotes.length)]);
    }
    
    private static void handleNaturalLanguage(String input) {
        String lower = input.toLowerCase();
        
        if (lower.contains("привет") || lower.contains("hello")) {
            System.out.println("Привет! Чем могу помочь?");
        } else if (lower.contains("как дела") || lower.contains("how are you")) {
            System.out.println("Отлично! Готов помочь с любыми задачами.");
        } else if (lower.contains("спасибо") || lower.contains("thank you")) {
            System.out.println("Пожалуйста! Всегда рад помочь.");
        } else if (lower.contains("что умеешь") || lower.contains("what can you do")) {
            showHelp();
        } else {
            System.out.println("Не понял команду. Введите 'help' для списка доступных команд.");
        }
    }
    
    private static void startBackgroundTasks() {
        executor.submit(() -> {
            while (running) {
                try {
                    Thread.sleep(30000);
                    if (memory.size() > 100) {
                        memory.clear();
                        System.out.println("\n[Система] Память очищена для оптимизации");
                    }
                } catch (InterruptedException e) {
                    break;
                }
            }
        });
    }
    
    private static void loadMemory() {
        try {
            Path memoryFile = Paths.get("ai_memory.txt");
            if (Files.exists(memoryFile)) {
                Files.lines(memoryFile).forEach(line -> {
                    String[] parts = line.split("=", 2);
                    if (parts.length == 2) {
                        memory.put(parts[0], parts[1]);
                    }
                });
                System.out.println("Память загружена: " + memory.size() + " записей");
            }
        } catch (Exception e) {
            System.out.println("Ошибка загрузки памяти: " + e.getMessage());
        }
    }
    
    private static void saveMemory() {
        try {
            Path memoryFile = Paths.get("ai_memory.txt");
            Files.write(memoryFile, memory.entrySet().stream()
                .map(entry -> entry.getKey() + "=" + entry.getValue())
                .collect(java.util.stream.Collectors.toList()));
            System.out.println("Память сохранена: " + memory.size() + " записей");
        } catch (Exception e) {
            System.out.println("Ошибка сохранения памяти: " + e.getMessage());
        }
    }
}