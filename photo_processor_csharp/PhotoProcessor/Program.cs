namespace PhotoProcessor.ConsoleApp
{
    // Importa los casos de uso de la capa de aplicación.
    using PhotoProcessor.Application.UseCases;
    // Importa las entidades y servicios del dominio.
    using PhotoProcessor.Domain.Entities;
    using PhotoProcessor.Domain.Services;
    // Importa las utilidades de infraestructura.
    using PhotoProcessor.Infrastructure.Utilities;
    // Importa librerías estándar de C#.
    using System;
    using System.IO;
    using System.Threading.Tasks; // Necesario para Task y async/await

    class Program
    {
        static async System.Threading.Tasks.Task Main(string[] args)
        {
            // Como usar: PhotoProcessor.exe "C:\FotosTests\Originales" "C:\FotosTests\Convertidas" 100 100 130
            // Argumentos esperados:
            // arg[0]: Ruta del directorio de entrada
            // arg[1]: Ruta del directorio de salida
            // arg[2] (opcional): Ancho de la foto (por defecto 400)
            // arg[3] (opcional): Alto de la foto (por defecto 400)
            // arg[4] (opcional): DPI (por defecto 300)

            if (args.Length < 2)
            {
                System.Console.WriteLine("Uso: PhotoProcessor.ConsoleApp <ruta_entrada> <ruta_salida> [ancho] [alto] [dpi]");
                System.Console.WriteLine("Ejemplo: PhotoProcessor.ConsoleApp \"C:\\fotos_originales\" \"C:\\fotos_procesadas\" 400 400 300");
                return;
            }

            string inputPath = args[0];
            string outputPath = args[1];

            int targetWidth = 400;
            int targetHeight = 400;
            int dpi = 300;

            // Intenta parsear los argumentos opcionales.
            if (args.Length >= 3 && int.TryParse(args[2], out int parsedWidth))
            {
                targetWidth = parsedWidth;
            }
            if (args.Length >= 4 && int.TryParse(args[3], out int parsedHeight))
            {
                targetHeight = parsedHeight;
            }
            if (args.Length >= 5 && int.TryParse(args[4], out int parsedDpi))
            {
                dpi = parsedDpi;
            }

            string haarCascadePath = AppSettings.GetHaarCascadePath();

            try
            {
                // Inyección de dependencias simple: se crean las instancias de las clases necesarias.
                var options = new ImageProcessingOptions(targetWidth, targetHeight, dpi, haarCascadePath);
                var imageProcessorService = new ImageProcessorService(options);
                var processImagesBatch = new ProcessImagesBatch(imageProcessorService);

                string[] allowedExtensions = { ".jpg", ".jpeg", ".png", ".bmp" };

                // Ejecuta el caso de uso principal.
                await processImagesBatch.Execute(inputPath, outputPath, allowedExtensions);
            }
            catch (System.IO.DirectoryNotFoundException ex)
            {
                System.Console.Error.WriteLine($"Error: {ex.Message}");
                System.Environment.Exit(1);
            }
            catch (System.InvalidOperationException ex)
            {
                System.Console.Error.WriteLine($"Error de configuración: {ex.Message}");
                System.Environment.Exit(1);
            }
            catch (System.ArgumentException ex)
            {
                System.Console.Error.WriteLine($"Error de argumento: {ex.Message}");
                System.Environment.Exit(1);
            }
            catch (Exception ex)
            {
                System.Console.Error.WriteLine($"Ha ocurrido un error inesperado: {ex.Message}");
                System.Environment.Exit(1);
            }

            System.Environment.Exit(0);
        }
    }
}