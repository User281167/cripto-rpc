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
import { IconMail } from "@tabler/icons-react";
import { useState } from "react";

import { SuscribeEmail } from "@/types/models";
import { suscribeEmail } from "@/api/email.api";

export const EmailSuscribe = () => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const [submitted, setSubmitted] = useState<SuscribeEmail | null>(null);
  const [time, setTime] = useState<TimeInputValue>();
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

    const formattedData: SuscribeEmail = {
      email: data.email as string,
      hour: time?.hour || 0,
      minute: time?.minute || 0,
    };

    // Clear errors and submit
    setErrors({});
    setSubmitted(formattedData);

    addToast({
      title: "Enviando suscripción",
      description: "Estamos enviando tu suscripción, por favor espera.",
      color: "primary",
      promise: suscribeEmail(formattedData)
        .then((res) => {
          if (res) {
            addToast({
              title: "Suscripción enviada",
              description: "Tu suscripción se ha enviado exitosamente.",
              color: "success",
            });
          } else {
            addToast({
              title: "Error al enviar la suscripción",
              description:
                "Tu suscripción no pudo ser enviada. Inténtalo de nuevo o más tarde.",
              color: "danger",
            });
          }
        })
        .catch(() => {
          addToast({
            title: "Error al enviar la suscripción",
            description:
              "Tu suscripción no pudo ser enviada. Inténtalo de nuevo o más tarde.",
            color: "danger",
          });
        }),
    });
  };

  return (
    <>
      <IconMail className="cursor-pointer hover:bg-gray-100" onClick={onOpen} />

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
                Suscribete a nuestro boletin para recibir actualizaciones a la
                hora que desees
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

                    <TimeInput
                      isRequired
                      onChange={setTime}
                      label="Hora de envío"
                    />

                    <div className="flex gap-4">
                      <Button
                        className="w-full"
                        color="primary"
                        type="submit"
                        onPress={onClose}
                      >
                        Suscribir
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
