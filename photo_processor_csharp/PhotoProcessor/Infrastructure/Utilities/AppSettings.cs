namespace PhotoProcessor.Infrastructure.Utilities
{
    using System;
    using System.IO;

    // Clase para manejar la configuración de la aplicación.
    public static class AppSettings
    {
        /// <summary>
        /// Obtiene la ruta completa al archivo Haar Cascade.
        /// </summary>
        /// <returns>La ruta del archivo Haar Cascade.</returns>
        public static string GetHaarCascadePath()
        {
            // Asume que el archivo haar cascade está en un subdirectorio 'haarcascades'
            // relativo al directorio de ejecución de la aplicación.
            string pathToExecutable = AppDomain.CurrentDomain.BaseDirectory;
            return Path.Combine(pathToExecutable, "haarcascades", "haarcascade_frontalface_default.xml");
        }
    }
}