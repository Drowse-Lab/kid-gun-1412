package kid_gun_1412.client;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

public final class MessageViewScreen extends Screen {
    private final String body;
    private final String signature;
    public MessageViewScreen(String body, String signature) {
        super(Component.translatable("screen.kid_gun_1412.message"));
        this.body = body;
        this.signature = signature;
    }
    @Override public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        int left = width / 2 - 128, top = height / 2 - 85;
        graphics.fill(left, top, left + 256, top + 170, 0xfff7f7f2);
        graphics.drawCenteredString(font, "MESSAGE", width / 2, top + 15, 0xff111111);
        int y = top + 42;
        for (net.minecraft.util.FormattedCharSequence line : font.split(Component.literal(body), 220)) {
            graphics.drawString(font, line, left + 18, y, 0xff202020, false);
            y += 10;
        }
        graphics.drawString(font, signature, left + 150, top + 145, 0xff202020, false);
        super.render(graphics, mouseX, mouseY, partialTick);
    }
    @Override public boolean isPauseScreen() { return false; }
}
