package kid_gun_1412;

import net.minecraftforge.fml.loading.FMLPaths;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

final class GunPackInstaller {
    private static final String RESOURCE = "/assets/kid_gun_1412/custom/kid_gun_1412.zip";

    private GunPackInstaller() {}

    static void install() {
        Path target = FMLPaths.GAMEDIR.get().resolve("tacz").resolve("kid_gun_1412.zip");
        try (InputStream input = GunPackInstaller.class.getResourceAsStream(RESOURCE)) {
            if (input == null) {
                KidGunMod.LOGGER.error("Bundled TaCZ gun pack is missing: {}", RESOURCE);
                return;
            }
            Files.createDirectories(target.getParent());
            Files.copy(input, target, StandardCopyOption.REPLACE_EXISTING);
            KidGunMod.LOGGER.info("Installed Kid Gun 1412 TaCZ pack: {}", target);
        } catch (IOException exception) {
            KidGunMod.LOGGER.error("Failed to install Kid Gun 1412 TaCZ pack", exception);
        }
    }
}
