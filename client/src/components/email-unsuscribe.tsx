import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  useDisclosure,
  Form,
  Input,
  TimeInput,
  TimeInputValue,
  addToast,
} from "@heroui/react";
import { IconMail, IconMailCancel } from "@tabler/icons-react";
import { useState } from "react";

import { SuscribeEmail } from "@/types/models";
import { suscribeEmail, unsuscribeEmail } from "@/api/email.api";

export const EmailUnsuscribe = () => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const [submitted, setSubmitted] = useState<string>(null);
  const [errors, setErrors] = useState({});

  const onSubmit = (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget));

    // Custom validation checks
    const newErrors = {};

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);

      return;
    }

    // Clear errors and submit
    setErrors({});
    setSubmitted(data.email as string);

    addToast({
      title: "Removiendo suscripción",
      description: "Estamos removiendo tu suscripción, por favor espera.",
      color: "primary",
      promise: unsuscribeEmail(data.email as string)
        .then((res) => {
          if (res) {
            addToast({
              title: "Suscripción removida",
              description: "Tu suscripción ha sido removida exitosamente.",
              color: "success",
            });
          } else {
            addToast({
              title: "Error al enviar la suscripción",
              description:
                "No pudimos remover tu suscripción. Inténtalo de nuevo o más tarde.",
              color: "danger",
            });
          }
        })
        .catch(() => {
          addToast({
            title: "Error al enviar la suscripción",
            description:
              "No pudimos remover tu suscripción. Inténtalo de nuevo o más tarde.",
            color: "danger",
          });
        }),
    });
  };

  return (
    <>
      <IconMailCancel
        className="cursor-pointer hover:bg-gray-100"
        onClick={onOpen}
      />

      <Modal
        isDismissable={false}
        isKeyboardDismissDisabled={true}
        isOpen={isOpen}
        onOpenChange={onOpenChange}
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                <IconMail />
                <h3 className="font-bold text-lg">Cancelar suscripción</h3>
              </ModalHeader>

              <ModalBody>
                <Form
                  className="w-full justify-center items-center space-y-4"
                  validationErrors={errors}
                  onReset={() => setSubmitted(null)}
                  onSubmit={onSubmit}
                >
                  <div className="flex flex-col gap-4 max-w-md">
                    <Input
                      isRequired
                      errorMessage={({ validationDetails }) => {
                        if (validationDetails.valueMissing) {
                          return "Por favor ingresa tu email";
                        }
                        if (validationDetails.typeMismatch) {
                          return "Por favor ingresa un email valido";
                        }
                      }}
                      label="Email"
                      labelPlacement="outside"
                      name="email"
                      placeholder="Email"
                      type="email"
                    />

                    <div className="flex gap-4">
                      <Button
                        className="w-full"
                        color="primary"
                        type="submit"
                        onPress={onClose}
                      >
                        Enviar
                      </Button>

                      <Button type="reset" variant="bordered">
                        Limpiar
                      </Button>
                    </div>
                  </div>
                </Form>
              </ModalBody>

              <ModalFooter>
                <Button color="danger" variant="light" onPress={onClose}>
                  Cerrar
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
};
