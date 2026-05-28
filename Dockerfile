FROM mcr.microsoft.com/dotnet/sdk:9.0 AS base
WORKDIR /app

# Устанавливаем chafa для терминальной графики, если она используется, а также toilet для шрифтов
RUN apt-get update && apt-get install -y chafa toilet figlet && rm -rf /var/lib/apt/lists/*

# Копируем только конфигурационные файлы (решение и нужные проекты)
COPY ParrotSlots.sln .
COPY src/ParrotSlots/ParrotSlots.csproj src/ParrotSlots/
COPY tests/ParrotSlots.Tests/ParrotSlots.Tests.csproj tests/ParrotSlots.Tests/

# Скачиваем зависимости конкретно для нашего решения
RUN dotnet restore ParrotSlots.sln

# Теперь копируем остальной исходный код
COPY . .

# Предварительно собираем проект, чтобы при run не тратилось на это время
RUN dotnet build src/ParrotSlots/ParrotSlots.csproj -c Release --no-restore

# Запускаем уже собранное приложение
ENTRYPOINT ["dotnet", "run", "--project", "src/ParrotSlots/ParrotSlots.csproj", "-c", "Release", "--no-build", "--no-restore", "--"]
CMD ["--terminal", "--chafa"]
