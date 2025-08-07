namespace PhotoProcessor.Infrastructure.Utilities
{
    using System;
    using System.IO;

    public static class AppSettings
    {
        /// <summary>
        /// Obtiene la ruta completa al archivo Haar Cascade.
        /// </summary>
        /// <returns>La ruta del archivo Haar Cascade.</returns>
        public static string GetHaarCascadePath()
        {
            string pathToExecutable = AppDomain.CurrentDomain.BaseDirectory;
            return Path.Combine(pathToExecutable, "haarcascades", "haarcascade_frontalface_default.xml");
        }
    }
}