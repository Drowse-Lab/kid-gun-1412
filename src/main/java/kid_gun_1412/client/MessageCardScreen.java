package kid_gun_1412.client;

import kid_gun_1412.CardData;
import kid_gun_1412.network.ModNetwork;
import kid_gun_1412.network.SaveMessageCardPacket;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;

public final class MessageCardScreen extends Screen {
    private final InteractionHand hand;
    private final String initialBody;
    private final String initialSignature;
    private EditBox body;
    private EditBox signature;
    private boolean editable;

    public MessageCardScreen(InteractionHand hand, ItemStack stack) {
        super(Component.translatable("screen.kid_gun_1412.message"));
        this.hand = hand;
        this.initialBody = stack.getOrCreateTag().getString(CardData.BODY);
        this.initialSignature = stack.getOrCreateTag().getString(CardData.SIGNATURE);
    }

    @Override
    protected void init() {
        editable = minecraft != null && CardData.canEdit(minecraft.player.getItemInHand(hand), minecraft.player.getUUID());
        int left = width / 2 - 128;
        int top = height / 2 - 85;
        body = addRenderableWidget(new EditBox(font, left + 16, top + 48, 224, 20,
                Component.translatable("screen.kid_gun_1412.body")));
        body.setMaxLength(256);
        body.setValue(initialBody);
        body.setEditable(editable);
        signature = addRenderableWidget(new EditBox(font, left + 96, top + 91, 144, 20,
                Component.translatable("screen.kid_gun_1412.signature")));
        signature.setMaxLength(32);
        signature.setValue(initialSignature);
        signature.setEditable(editable);
        if (editable) addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> saveAndClose())
                .bounds(width / 2 - 45, top + 128, 90, 20).build());
        setInitialFocus(body);
    }

    private void saveAndClose() {
        ModNetwork.CHANNEL.sendToServer(new SaveMessageCardPacket(hand, body.getValue(), signature.getValue()));
        onClose();
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        int left = width / 2 - 128;
        int top = height / 2 - 85;
        graphics.fill(left, top, left + 256, top + 145, 0xfff7f7f2);
        graphics.fill(left, top, left + 256, top + 3, 0xff202020);
        graphics.fill(left, top + 142, left + 256, top + 145, 0xff202020);
        graphics.drawCenteredString(font, "MESSAGE", width / 2, top + 15, 0xff111111);
        graphics.drawString(font, Component.translatable("screen.kid_gun_1412.body"), left + 16, top + 36, 0xff333333, false);
        graphics.drawString(font, Component.translatable("screen.kid_gun_1412.signature"), left + 16, top + 97, 0xff333333, false);
        if (!editable) graphics.drawCenteredString(font, Component.translatable("screen.kid_gun_1412.read_only"), width / 2, top + 126, 0xff777777);
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
