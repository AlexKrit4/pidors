FROM mcr.microsoft.com/dotnet/sdk:9.0 AS base
WORKDIR /app

# Install terminal graphics and text rendering tools.
RUN apt-get update && apt-get install -y chafa toilet figlet && rm -rf /var/lib/apt/lists/*

# Copy project files first to cache NuGet restore.
COPY ParrotSlots.sln .
COPY src/ParrotSlots/ParrotSlots.csproj src/ParrotSlots/
COPY tests/ParrotSlots.Tests/ParrotSlots.Tests.csproj tests/ParrotSlots.Tests/

RUN dotnet restore ParrotSlots.sln

# Copy source after restore. .dockerignore keeps host bin/obj out of the image.
COPY . .

RUN dotnet build src/ParrotSlots/ParrotSlots.csproj -c Release --no-restore

ENTRYPOINT ["dotnet", "run", "--project", "src/ParrotSlots/ParrotSlots.csproj", "-c", "Release", "--no-build", "--no-restore", "--"]
CMD ["--terminal", "--chafa"]
